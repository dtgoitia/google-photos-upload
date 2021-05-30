from __future__ import annotations

import logging
from pathlib import Path

from gpy.adb import ANDROID_STORAGE, AQUARIS_PRO_X, adb_push, assert_is_device_connected
from gpy.config import MEDIA_DIR
from gpy.filesystem import get_paths_recursive
from gpy.log import get_log_format, get_logs_output_path

logger = logging.getLogger(__name__)


def build_destination_uri(local: Path) -> Path:
    file_name = local.name
    dir_name = local.parent.name.replace(" ", "_").replace("(", "").replace(")", "")
    remote = ANDROID_STORAGE / dir_name / file_name
    return remote


def push_files_to_phone() -> None:
    assert_is_device_connected(device_id=AQUARIS_PRO_X)

    all_media_paths = get_paths_recursive(root_path=MEDIA_DIR)

    for path in all_media_paths:
        logger.info(f"Converting to mp4 for {path}")
        uri = build_destination_uri(path)
        adb_push(local=path, remote=uri)
        logger.info(f"Success converting {path} to mp4")


if __name__ == "__main__":
    logs_path = get_logs_output_path()
    log_format = get_log_format()
    logging.basicConfig(filename=logs_path, format=log_format, level=logging.DEBUG)

    logger.info("Adding metadata to pictures")
    push_files_to_phone()
    logger.info("Finished adding metadata to pictures")
