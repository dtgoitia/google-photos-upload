from __future__ import annotations

import logging

from gpy.config import MEDIA_DIR
from gpy.ffmpeg import path_to_mp4
from gpy.filesystem import get_paths_recursive
from gpy.log import get_log_format, get_logs_output_path

logger = logging.getLogger(__name__)


def refresh_google_spreadsheet_to_latest_state() -> None:
    all_media_paths = get_paths_recursive(root_path=MEDIA_DIR)
    avi_paths = (p for p in all_media_paths if p.suffix.lower() == ".avi")

    for path in avi_paths:
        logger.info(f"Converting to mp4 for {path}")
        path_to_mp4(path, backup=False)
        logger.info(f"Success converting {path} to mp4")


if __name__ == "__main__":
    logs_path = get_logs_output_path()
    log_format = get_log_format()
    logging.basicConfig(filename=logs_path, format=log_format, level=logging.DEBUG)

    logger.info("Converting AVI files to MP4")
    refresh_google_spreadsheet_to_latest_state()
    logger.info("Finished converting AVI files to MP4")
