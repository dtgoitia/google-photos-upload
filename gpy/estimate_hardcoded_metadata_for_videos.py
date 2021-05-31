from __future__ import annotations

import itertools
import logging
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from turtle import st
from typing import List

import pytz
from click import Tuple

from gpy.cli.add_google_timestamp import add_metadata_to_single_file
from gpy.cli.refresh_gsheet import convert_to_local_plain_text_spreadsheet
from gpy.cli.scan import scan_date
from gpy.config import DEFAULT_TZ, MEDIA_DIR, RECONCILE_DRY_RUN, TABLE_AS_STRING_PATH
from gpy.exiftool import client as exiftool
from gpy.filenames import build_file_id
from gpy.filenames import parse_datetime as datetime_parser
from gpy.filesystem import get_paths_recursive, is_video, read_table, save_table
from gpy.log import get_log_format, get_logs_output_path
from gpy.types import FileReportFromTable

logger = logging.getLogger(__name__)


def find_next_picture_index(table: List[FileReportFromTable], start: int) -> int:
    """From 'start' index, find the next index where there is a picture - which should
    have a google-like timestamp."""
    ...
    # assert found picture has metadata, if not, fail, all pictures must have google metadata at this point


def interpolate_dates(amount: int, start: datetime, end: datetime) -> List[datetime]:
    assert isinstance(amount, int), f"Amount ({amount}) must be int"
    assert isinstance(start, datetime), f"Start ({start}) must be datetime.datetime"
    assert isinstance(end, datetime), f"End ({end}) must be datetime.datetime"

    start_epoch = start.timestamp()
    end_epoch = end.timestamp()
    delta = (end_epoch - start_epoch) / (amount + 1)

    epoch_intervals = []
    cursor = start_epoch
    for _ in range(amount):
        next_epoch = cursor + delta
        epoch_intervals.append(next_epoch)
        cursor = next_epoch

    utc_timestamps = [datetime.fromtimestamp(epoch) for epoch in epoch_intervals]
    timestamps = [t.astimezone(pytz.utc).astimezone(DEFAULT_TZ) for t in utc_timestamps]
    timestamps_without_ms = [t.replace(microsecond=0) for t in timestamps]
    return timestamps_without_ms


def add_date_to_video(
    video: FileReportFromTable, date: datetime
) -> FileReportFromTable:
    updated_video = FileReportFromTable(
        file_id=video.file_id,
        path=video.path,
        filename_date=video.filename_date,
        metadata_date=video.metadata_date,
        dates_match=video.dates_match,
        gphotos_compatible_metadata=date,  # this is the only relevant edit
        ready_to_upload=video.ready_to_upload,
        uploaded=video.uploaded,
        add_google_timestamp=video.add_google_timestamp,
        convert_to_mp4=video.convert_to_mp4,
        upload_in_next_reconcile=video.upload_in_next_reconcile,
    )
    return updated_video


def estimate_video_date_from_dir_name(row: FileReportFromTable) -> datetime:
    dir_name = row.path.parent.name
    matches = re.search(r"(20[0-9]{2})-([0-9]{2})-([0-9]{2})", dir_name)
    year = int(matches.group(1))
    month = int(matches.group(2))
    day = int(matches.group(3))
    estimated_utc_datetime = datetime(year, month, day, 8, 0, 0, tzinfo=pytz.utc)
    estimated_datetime = estimated_utc_datetime.astimezone(DEFAULT_TZ)
    return estimated_datetime


def get_next_minute(reference: datetime) -> datetime:
    result = reference.replace(
        minute=reference.minute + 1,
        second=0,
        microsecond=0,
    )
    return result


def estimate_datetime_for_videos_in_folder(table: List[FileReportFromTable]) -> None:
    assert len(table) > 0, "Something went wrong, there are no rows in this subtable"
    directories = {file.path.parent for file in table}
    assert len(directories) != 0, "Something went wrong, there are no dirs in the table"
    assert len(directories) == 1, f"Rows must be of the same directory: {directories}"

    updated_table = [None] * len(table)  # create empty table
    last_picture_index = None
    videos_to_estimate = []
    indexes_of_videos_to_estimate = []
    estimated_initial_date = None
    logger.info("Checking each item in table...")
    for i, row in enumerate(table):
        is_picture = row.path.suffix.lower() == ".jpg"

        # Picture with date, no videos to estiamte yet
        if is_picture and not indexes_of_videos_to_estimate:
            logger.info(f"{row.path} is picture, and there are no videos to estimate")
            updated_table[i] = row
            last_picture_index = i
            continue

        is_video = not is_picture  # it might be an image in a non JPG format
        if is_video:
            logger.info(f"{row.path} is video")
            is_mp4 = row.path.suffix == ".mp4"
            assert is_mp4, f"{row.path} is not mp4, please convert first"

            videos_to_estimate.append(row)
            indexes_of_videos_to_estimate.append(i)

            is_last_row_in_table = i == len(table) - 1
            if is_last_row_in_table:
                if last_picture_index is None:
                    # you've found the last video of a folder where all the files are
                    # videos, just estimate from date in folder name
                    start_date = estimate_video_date_from_dir_name(row)
                    estimated_initial_date = start_date
                else:
                    last_picture: FileReportFromTable = table[last_picture_index]
                    start_date = last_picture.gphotos_compatible_metadata

                for video_index, video in enumerate(videos_to_estimate):
                    table_index = indexes_of_videos_to_estimate[video_index]
                    next_minute = get_next_minute(start_date)
                    updated_video = add_date_to_video(video=video, date=next_minute)
                    updated_table[table_index] = updated_video
                break
            else:
                # it's not the last element in the list, carry on
                continue

        # Picture with date, but there are videos to estiamte yet
        if is_picture and len(indexes_of_videos_to_estimate) > 0:
            required_date_amount = len(indexes_of_videos_to_estimate)
            logger.info(
                f"{row.path} is picture, and there are {required_date_amount} videos to"
                " estimate"
            )

            # Interpolate dates
            if last_picture_index is None:  # there are no videos before the pictures!
                if estimated_initial_date:
                    start_date = estimated_initial_date
                else:
                    start_date = estimate_video_date_from_dir_name(row)
                    estimated_initial_date = start_date
            else:  # usual situation
                last_picture: FileReportFromTable = table[last_picture_index]
                start_date = last_picture.gphotos_compatible_metadata
            end_date = row.gphotos_compatible_metadata
            datetimes = interpolate_dates(required_date_amount, start_date, end_date)

            # Assign dates to videos
            for video_index, video_datetime in enumerate(datetimes):
                video = videos_to_estimate[video_index]
                updated_video = add_date_to_video(video, video_datetime)

                # Add updated video to table in the right place
                if last_picture_index is None:
                    # Hack explanation: the -1 is because if the are no pictures before
                    # the video, you need table_index to be 0, and putting a -1 is the
                    # way to fix this issue
                    last_picture_index = -1
                table_index = last_picture_index + 1 + video_index

                updated_table[table_index] = updated_video

            # Add picture after interpolation
            updated_table[i] = row

            # Update buffers
            last_picture_index = i
            videos_to_estimate = []
            indexes_of_videos_to_estimate = []

    # Check there are no None rows
    for i, row in enumerate(updated_table):
        # if row is None:
        #     breakpoint()
        assert row is not None, f"Row {i} is None"

    return updated_table


def split_table_per_directories(
    table: List[FileReportFromTable],
) -> List[List[FileReportFromTable]]:
    directory_to_rows_map = defaultdict(list)
    for row in table:
        dir = row.path.parent
        directory_to_rows_map[dir].append(row)

    tables_per_directory = list(directory_to_rows_map.values())

    return tables_per_directory


def concatenate_subtables(
    subtables: List[List[FileReportFromTable]],
) -> List[FileReportFromTable]:
    merged_table = list(itertools.chain.from_iterable(subtables))
    return merged_table


def estimate_hardcoded_metadata_for_videos_across_all_folders() -> None:
    logger.info(f"Reading table at {TABLE_AS_STRING_PATH}")
    table = read_table(path=TABLE_AS_STRING_PATH)

    tables_per_dir = split_table_per_directories(table)
    updated_tables_per_dir = [
        estimate_datetime_for_videos_in_folder(table_per_dir)
        for table_per_dir in tables_per_dir
    ]
    updated_table = concatenate_subtables(updated_tables_per_dir)

    # NOTE: for debugging
    output_path = TABLE_AS_STRING_PATH.parent / f"{TABLE_AS_STRING_PATH.name}_estimated"
    # output_path = TABLE_AS_STRING_PATH
    updated_table_as_str = convert_to_local_plain_text_spreadsheet(updated_table)
    save_table(path=output_path, data=updated_table_as_str)


if __name__ == "__main__":
    logs_path = get_logs_output_path()
    log_format = get_log_format()
    logging.basicConfig(filename=logs_path, format=log_format, level=logging.DEBUG)

    logger.info("Adding hardcoded metadata to videos")
    estimate_hardcoded_metadata_for_videos_across_all_folders()
    logger.info("Finished adding hardcoded metadata to videos")
