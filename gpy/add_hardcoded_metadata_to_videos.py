from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import pytz

from gpy.cli.add_google_timestamp import add_metadata_to_single_file
from gpy.cli.scan import scan_date
from gpy.config import DEFAULT_TZ, MEDIA_DIR, RECONCILE_DRY_RUN, TABLE_AS_STRING_PATH
from gpy.exiftool import client as exiftool
from gpy.filenames import build_file_id
from gpy.filenames import parse_datetime as datetime_parser
from gpy.filesystem import get_paths_recursive, is_video, read_table
from gpy.log import get_log_format, get_logs_output_path

logger = logging.getLogger(__name__)


def add_hardcoded_metadata_to_video(path: Path, hardcoded_datetime: datetime) -> None:
    """Hardcoded metadata will be read from metadata_datetime, not google_datetime."""
    logger.info(f"Editing datetime in medatata for {path}")
    assert hardcoded_datetime, f"a hardcoded datetime is required"
    # reports = scan_date(exiftool, datetime_parser, path)
    # report = reports[0]
    # if report.google_date is not None:
    #     logger.warning(f"Google date already exists in {path}, will do nothing")
    #     return

    ts_in_utc = hardcoded_datetime.astimezone(pytz.utc)
    ts = ts_in_utc.astimezone(DEFAULT_TZ)

    if RECONCILE_DRY_RUN is False:
        add_metadata_to_single_file(path=path, iso_timestamp=ts.isoformat())
    logger.info(f"Successfully edited {path}")


def add_hardcoded_metadata_to_videos() -> None:
    all_media_paths = get_paths_recursive(root_path=MEDIA_DIR)
    videos_paths = [p for p in all_media_paths if is_video(p)]

    # The edition is idempotent, but it's slow to recheck files, so just try to fail early if possible
    for video_path in videos_paths:
        is_mp4 = video_path.suffix.lower() == ".mp4"
        assert is_mp4, f"{video_path} is not mp4, please convert all videos files first"

    logger.info(f"Reading table at {TABLE_AS_STRING_PATH}")
    table = read_table(path=TABLE_AS_STRING_PATH)
    logger.info("Indexing table...")
    indexed_table = {file.path: file for file in table}
    logger.info("Table successfully indexed")

    for path in videos_paths:
        if path not in indexed_table:
            logger.warning(f"Video {path} not found in table, please refresh")
        hardcoded_datetime = indexed_table[path].gphotos_compatible_metadata
        assert hardcoded_datetime, f"No hardcoded datetime for {path}, please add one"
        logger.info(f"Adding GPhotos compatible datetime to {path}")
        add_hardcoded_metadata_to_video(path, hardcoded_datetime)
        logger.info(f"Success adding GPhotos compatible datetime to {path}")


if __name__ == "__main__":
    logs_path = get_logs_output_path()
    log_format = get_log_format()
    logging.basicConfig(filename=logs_path, format=log_format, level=logging.DEBUG)

    logger.info("Adding hardcoded metadata to videos")
    add_hardcoded_metadata_to_videos()
    logger.info("Finished adding hardcoded metadata to videos")
