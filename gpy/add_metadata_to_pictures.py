from __future__ import annotations

import logging
from pathlib import Path

import pytz

from gpy.cli.add_google_timestamp import add_metadata_to_single_file
from gpy.cli.scan import scan_date
from gpy.config import DEFAULT_TZ, MEDIA_DIR, RECONCILE_DRY_RUN
from gpy.exiftool import client as exiftool
from gpy.filenames import parse_datetime as datetime_parser
from gpy.filesystem import get_paths_recursive, is_video
from gpy.log import get_log_format, get_logs_output_path

logger = logging.getLogger(__name__)


def add_metadata_to_picture(path: Path) -> None:
    logger.info(f"Editing datetime in medatata for {path}")
    reports = scan_date(exiftool, datetime_parser, path)
    report = reports[0]
    if report.google_date is not None:
        logger.warning(f"Google date already exists in {path}, will do nothing")
        return

    ts_in_utc = report.metadata_date.astimezone(pytz.utc)
    ts = ts_in_utc.astimezone(DEFAULT_TZ)

    if RECONCILE_DRY_RUN is False:
        add_metadata_to_single_file(path=path, iso_timestamp=ts.isoformat())
    logger.info(f"Successfully edited {path}")


def add_metadata_to_pictures() -> None:
    all_media_paths = get_paths_recursive(root_path=MEDIA_DIR)
    pictures_paths = (p for p in all_media_paths if not is_video(p))

    for path in pictures_paths:
        logger.info(f"Converting to mp4 for {path}")
        add_metadata_to_picture(path)
        logger.info(f"Success converting {path} to mp4")


if __name__ == "__main__":
    logs_path = get_logs_output_path()
    log_format = get_log_format()
    logging.basicConfig(filename=logs_path, format=log_format, level=logging.DEBUG)

    logger.info("Adding metadata to pictures")
    add_metadata_to_pictures()
    logger.info("Finished adding metadata to pictures")
