from __future__ import annotations

import datetime
import logging
from pathlib import Path
from typing import List

import attr
import gspread
import pytz

from gpy.cli.add_google_timestamp import add_metadata_to_single_file
from gpy.cli.meta import edit_metadata_datetime
from gpy.cli.scan import scan_date
from gpy.config import AGGREGATED_MEDIA_INFO_DIR, DEFAULT_TZ
from gpy.exiftool import client as exiftool
from gpy.filenames import parse_datetime as datetime_parser
from gpy.filesystem import read_aggregated_reports
from gpy.google_sheet import GSheetRow, Worksheet, fetch_worksheet
from gpy.gphotos import GooglePhotosClient, upload_media
from gpy.log import get_log_format, get_logs_output_path

USE_ACTIONS_IN_GSHEET = True
DRY_RUN = False

DO_NOTHING = "DO_NOTHING"  # This action does nothing on the file
UPLOAD = "UPLOADJ"  # Action representing uploading a media to GPhotos
EDIT_METADATA_DATETIME = "EDIT_METADATA_DATETIME"


@attr.s(auto_attribs=True, frozen=True)
class AggregatedMediaReportPath:
    path: Path
    created_on: datetime.datetime

    @classmethod
    def from_path(cls, path: Path) -> AggregatedMediaReportPath:
        _, timestamp_as_str = path.stem.split("__")

        created_on = datetime.datetime.fromisoformat(timestamp_as_str)

        return cls(path=path, created_on=created_on)


@attr.s(auto_attribs=True, frozen=True)
class Action:
    """Declaration of an action that should be applied.

    Action examples:
        - add timestamp to file
        - upload file
    """

    type: str
    path: Path


@attr.s(auto_attribs=True, frozen=True)
class AppliedAction:
    """Data obtained as a result of applying an Action."""

    action: Action
    success: bool


def get_file_aggregated_reports_path() -> Path:
    json_paths = AGGREGATED_MEDIA_INFO_DIR.glob("*.json")
    parsed_paths = map(AggregatedMediaReportPath.from_path, json_paths)

    most_recent_report: AggregatedMediaReportPath = next(parsed_paths)
    for report in parsed_paths:
        if most_recent_report.created_on < report.created_on:
            most_recent_report = report

    return most_recent_report.path


def read_latest_local_gsheet() -> Worksheet:
    path = get_file_aggregated_reports_path()
    reports = read_aggregated_reports(path)
    worksheet = {report.file_id: report.to_gsheet_row() for report in reports}
    return worksheet


def read_latest_remote_gsheet() -> Worksheet:
    logger.info("Authenticating with Google Spreadsheet API...")
    gc = gspread.oauth()

    spreadsheet_name = "Photo backup tracker"
    sh = gc.open(spreadsheet_name)

    logger.info(f"Fetching data from the {spreadsheet_name!r} spreadsheet...")
    worksheet = fetch_worksheet(sh)
    logger.info(f"Successfully fetched data from the {spreadsheet_name!r} spreadsheet")

    return worksheet


def determine_action_manually(local: GSheetRow, remote: GSheetRow) -> Action:
    file_id = local.file_id
    path = local.path
    logger.info(f"Determining action for {file_id!r}")
    if remote.upload_in_next_reconcile:
        return Action(type=UPLOAD, path=path)

    if remote.add_google_timestamp:
        logger.info(f"Action: EDIT_METADATA_DATETIME for file {file_id!r}")
        return Action(type=EDIT_METADATA_DATETIME, path=path)

    logger.info(f"Action: DO_NOTHING for file {file_id!r}")
    return Action(type=DO_NOTHING, path=path)


def determine_action_automatically(local: GSheetRow, remote: GSheetRow) -> Action:
    file_id = local.file_id
    path = local.path
    logger.info(f"Determining action for {file_id!r}")
    if remote.upload_in_next_reconcile:
        if local.uploaded:
            logger.debug(
                f"{file_id} was marked to be uploaded in the next reconcile but it is"
                " also marked as uploaded. No need to re-upload, so do nothing"
            )
            return Action(type=DO_NOTHING, path=path)

        if not local.uploaded and not local.ready_to_upload:
            logger.debug(
                f"{file_id} was marked to be uploaded in the next reconcile but it is"
                " not ready to be uploaded. Add metadata"
            )
            return Action(type=EDIT_METADATA_DATETIME, path=path)

        # TODO: worth being defensive and ensure that datetimes are ready to go?
        # yes, but only if you make exiftool work smoothly <======================================== NEXT BIT
        logger.info(f"Action: UPLOAD for file {file_id!r}")
        return Action(type=UPLOAD, path=path)

    if not local.uploaded and not local.ready_to_upload:
        logger.info(f"Action: EDIT_METADATA_DATETIME for file {file_id!r}")
        return Action(type=EDIT_METADATA_DATETIME, path=path)

    logger.info(f"Action: DO_NOTHING for file {file_id!r}")
    return Action(type=DO_NOTHING, path=path)


def determine_actions(local: Worksheet, remote: Worksheet) -> List[Action]:
    # local: local copy of the GSheet state, which has been pushed in the past to the cloud
    # remote: most up to date GSheet state

    assert local
    assert remote

    local_file_ids = set(local.keys())
    remote_file_ids = set(remote.keys())

    # overlapping = the file_id is present in both local and remote
    overlapping_file_ids = local_file_ids.intersection(remote_file_ids)

    actions: List[Action] = []
    for file_id in overlapping_file_ids:
        local_file = local[file_id]
        remote_file = remote[file_id]
        if USE_ACTIONS_IN_GSHEET is True:
            action = determine_action_manually(local_file, remote_file)
        else:
            action = determine_action_automatically(local_file, remote_file)
        actions.append(action)

    return actions


def reconcile() -> None:
    client = GooglePhotosClient()
    client.start_session()

    # TODO: get a session
    def apply_action(action: Action) -> AppliedAction:
        # Here you will need to actually edit files
        # ensure edited files are copied to /tmp/var or so before uploading, and log
        # the tmp paths for debugging

        success = False
        target_tz = DEFAULT_TZ

        path = action.path
        if action.type == UPLOAD:
            logger.info(f"Uploading {path}")
            try:
                if DRY_RUN is False:
                    upload_media(session=client._session, path=path)
                success = True
                logger.info("Successfully uploaded")
            except Exception as e:
                print(e)
                print("something went wrong... is it worth handling it?")
                breakpoint()
        elif action.type == EDIT_METADATA_DATETIME:
            logger.info(f"Editing datetime in medatata for {path}")
            try:
                reports = scan_date(exiftool, datetime_parser, path)
                report = reports[0]
                assert report.google_date is None
                ts_in_utc = report.metadata_date.astimezone(pytz.utc)
                ts = ts_in_utc.astimezone(target_tz)
                if DRY_RUN is False:
                    add_metadata_to_single_file(
                        path=path,
                        iso_timestamp=ts.isoformat(),
                    )
                success = True
                logger.info("Successfully edited")
            except Exception as e:
                print(e)
                print("something went wrong... is it worth handling it?")
                breakpoint()
        elif action.type == DO_NOTHING:
            logger.info(f"No action for {path}")
            success = True
        else:
            logger.warning(f"")
            breakpoint()
            raise NotImplementedError("Unexpected situation happened!")

        applied_action = AppliedAction(action=action, success=success)

        return applied_action

    local = read_latest_local_gsheet()
    remote = read_latest_remote_gsheet()
    actions = determine_actions(local, remote)
    # TODO: worth persisting actions before executing?
    if DRY_RUN is False:
        applied_actions = list(map(apply_action, actions))
    # update gsheet? probably worth letting the 'refresh' bit to be done manually
    # in git when you push, your local state updates, no need to refetch :/
    # hmm... maybe do it automatically
    assert applied_actions


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    logs_path = get_logs_output_path()
    log_format = get_log_format()
    logging.basicConfig(filename=logs_path, format=log_format, level=logging.DEBUG)

    logger.info("Refreshing Google Spreadsheet to show latest state")
    reconcile()
    logger.info("Finished refreshing Google Spreadsheet to show latest state")
