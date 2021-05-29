from __future__ import annotations

import datetime
import logging
from pathlib import Path
from typing import List, Set

import attr
import gspread

from gpy.cli.report_uploaded import fetch_uploaded_media_info_between_dates
from gpy.cli.scan import scan_date
from gpy.config import (
    AGGREGATED_MEDIA_INFO_DIR,
    DEFAULT_TZ,
    LOCAL_MEDIA_INFO_DIR,
    MEDIA_DIR,
    UPLOADED_MEDIA_INFO_DIR,
    USE_LAST_REPORT_ON_REFRESH,
)
from gpy.exiftool import client as exiftool_client
from gpy.filenames import build_file_id
from gpy.filenames import parse_datetime as datetime_parser
from gpy.filesystem import read_reports, write_json, write_reports
from gpy.google_sheet import (
    FileId,
    FileReport,
    fetch_worksheet,
    merge,
    upload_worksheet,
)
from gpy.gphotos import MediaItem, read_media_items
from gpy.log import get_log_format, get_logs_output_path
from gpy.types import FileDateReport, unstructure

logger = logging.getLogger(__name__)

IsUploaded = bool


def read_uploaded_media_report(path: Path) -> List[MediaItem]:
    items = read_media_items(path)
    return items


def get_uploaded_file_ids(media_items: List[MediaItem]) -> Set[FileId]:
    file_ids: Set[FileId] = set()

    for media_item in media_items:
        file_id = build_file_id(
            file_name=media_item.filename,
            timestamp=media_item.media_metadata.creation_time,
        )

        if file_id in file_ids:
            logger.error(f"{file_id!r} file ID is duplicated, find a better key")
            breakpoint()

        file_ids.add(file_id)

    return file_ids


def get_updated_state(
    uploaded_file_ids: Set[FileId],
    local_files: List[FileDateReport],
) -> List[FileReport]:
    file_report = []
    for date_report in local_files:
        timestamp = date_report.metadata_date or date_report.filename_date
        file_id = build_file_id(date_report.path.name, timestamp)
        is_uploaded = file_id in uploaded_file_ids

        row = FileReport(
            file_id=file_id,
            path=date_report.path,
            filename_date=date_report.filename_date,
            metadata_date=date_report.metadata_date,
            dates_match=date_report.dates_match,
            gphotos_compatible_metadata=date_report.google_date,
            ready_to_upload=date_report.is_ready_to_upload,
            uploaded=is_uploaded,
            add_google_timestamp=False,
            convert_to_mp4=False,
            upload_in_next_reconcile=False,
        )
        file_report.append(row)

    return file_report


def add_timezone(report: FileDateReport, tz=DEFAULT_TZ) -> FileDateReport:
    if report.filename_date:
        filename_date = tz.localize(report.filename_date)
    else:
        filename_date = None

    if report.metadata_date:
        metadata_date = tz.localize(report.metadata_date)
    else:
        metadata_date = None

    if report.google_date:
        google_date = tz.localize(report.google_date)
    else:
        google_date = None

    tz_aware_report = FileDateReport(
        path=report.path,
        filename_date=filename_date,
        metadata_date=metadata_date,
        google_date=google_date,
        gps=report.gps,
    )

    return tz_aware_report


@attr.s(auto_attribs=True, frozen=True)
class UploadedMediaInfoPath:
    start: datetime.datetime
    end: datetime.datetime
    path: Path
    created_on: datetime.datetime

    @classmethod
    def from_path(cls, path: Path) -> UploadedMediaInfoPath:
        _, date_range, timestamp_as_str = path.stem.split("__")

        start, end = map(datetime.datetime.fromisoformat, date_range.split("_"))
        created_on = datetime.datetime.fromisoformat(timestamp_as_str)

        return cls(start=start, end=end, path=path, created_on=created_on)


def get_last_report_gphotos_path(
    start: datetime.datetime, end: datetime.datetime
) -> Path:
    def matches_dates(path: UploadedMediaInfoPath) -> bool:
        return path.start == start and path.end == end

    json_paths = UPLOADED_MEDIA_INFO_DIR.glob("*.json")
    parsed_paths = map(UploadedMediaInfoPath.from_path, json_paths)
    paths_of_interest = filter(matches_dates, parsed_paths)

    most_recent_report: UploadedMediaInfoPath = next(paths_of_interest)
    for report in paths_of_interest:
        if most_recent_report.created_on < report.created_on:
            most_recent_report = report

    return most_recent_report.path


@attr.s(auto_attribs=True, frozen=True)
class LocalMediaReportPath:
    path: Path
    created_on: datetime.datetime

    @classmethod
    def from_path(cls, path: Path) -> UploadedMediaInfoPath:
        _, timestamp_as_str = path.stem.split("__")

        created_on = datetime.datetime.fromisoformat(timestamp_as_str)

        return cls(path=path, created_on=created_on)


def get_last_local_report_path() -> Path:
    json_paths = LOCAL_MEDIA_INFO_DIR.glob("*.json")
    parsed_paths = map(LocalMediaReportPath.from_path, json_paths)

    most_recent_report: LocalMediaReportPath = next(parsed_paths)
    for report in parsed_paths:
        if most_recent_report.created_on < report.created_on:
            most_recent_report = report

    return most_recent_report.path


def build_local_file_report_path() -> Path:
    now = datetime.datetime.now().isoformat()
    return LOCAL_MEDIA_INFO_DIR / f"local_media_date_info__{now}.json"


def build_local_file_report() -> Path:
    # Equivalent to:
    # python -m gpy --debug scan date --report foo.json to_backup_in_gphotos
    logger.info(f"Scanning file datetimes in {MEDIA_DIR}")
    reports = scan_date(exiftool_client, datetime_parser, MEDIA_DIR)
    logger.info("Scan completed")

    # Do not add tz
    # GSheet should show what you have locally, with or without timezone
    # When you reconcile, you can add the right timezone
    # logger.info("Adding timezone data if required")
    # reports_with_tz = list(map(add_timezone, reports))

    report_path = build_local_file_report_path()
    write_reports(path=report_path, reports=reports)
    return report_path


def build_file_report_path() -> Path:
    now = datetime.datetime.now().isoformat()
    return AGGREGATED_MEDIA_INFO_DIR / f"local_media_info__{now}.json"


def save_file_aggregated_reports(reports: List[FileReport]) -> None:
    path = build_file_report_path()
    data = unstructure(reports)

    logger.info(f"Storing file aggregated reports at {path}")
    write_json(path=path, content=data)

    return path


def refresh_google_spreadsheet_to_latest_state() -> None:
    # start = datetime.datetime(2005, 6, 1)
    # end = datetime.datetime(2007, 1, 1)

    # # check what's in GPhotos
    # if True:  # you really don't care about what's uploaded... ¬¬
    #     uploaded_media_info_path = get_last_report_gphotos_path(start, end)
    # else:
    #     uploaded_media_info_path = fetch_uploaded_media_info_between_dates(start, end)
    # uploaded_media_items = read_uploaded_media_report(uploaded_media_info_path)
    # uploaded_file_ids = get_uploaded_file_ids(uploaded_media_items)
    uploaded_file_ids = set()

    # check what's is localy - ready to upload or not
    if USE_LAST_REPORT_ON_REFRESH:
        local_files_report_path = get_last_local_report_path()
    else:
        local_files_report_path = build_local_file_report()
    current_local_files = read_reports(local_files_report_path)

    # rebuild new GSheet state
    file_aggregated_reports = get_updated_state(uploaded_file_ids, current_local_files)

    # store new GSheet state localy with timestamp
    save_file_aggregated_reports(file_aggregated_reports)

    # Pushing new state to GSheet
    logger.info("Authenticating with Google Spreadsheet API...")
    gc = gspread.oauth()

    spreadsheet_name = "Photo backup tracker"
    sh = gc.open(spreadsheet_name)

    logger.info(f"Fetching data from the {spreadsheet_name!r} spreadsheet...")
    worksheet = fetch_worksheet(sh)

    logger.info("Merging report data with the spreadsheet...")
    updated_gsheet = merge(worksheet, file_aggregated_reports)

    logger.info("Uploading updated data to the spreadsheet...")
    upload_worksheet(sh, updated_gsheet)
    logger.info("Report upload successfuly completed")

    # TODO: in the `reconcile` command, read state from GSheet - which has been manually updated
    # TODO: check local state, compare with GSheet
    # TODO: apply required changes to change local state to GSheet
    # TODO: update GSheet with achieved changes (don't update unachieved changes in
    # GSheet, but log missing unachieved changes and why it was not possible to achieve them)

    # Keep log of what has been uploaded when in a log file


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    logs_path = get_logs_output_path()
    log_format = get_log_format()
    logging.basicConfig(filename=logs_path, format=log_format, level=logging.DEBUG)

    logger.info("Refreshing Google Spreadsheet to show latest state")
    refresh_google_spreadsheet_to_latest_state()
    logger.info("Finished refreshing Google Spreadsheet to show latest state")
