import logging
from pathlib import Path
from typing import Iterator

logger = logging.getLogger(__name__)


def is_supported(path: Path) -> bool:
    return path.suffix.lower() in (".jpg", ".png", ".mp4", ".3gp")


def get_paths_recursive(*, root_path: Path) -> Iterator[Path]:
    """Yield absolute path of supported files under root_path.

    Refer to is_supported() for further information on supported files.
    """
    logger.debug(f"Recursivelly looking for files in {root_path}")

    if root_path.is_file():
        if is_supported(root_path):
            logger.debug(f"{root_path} is a supported file")
            yield root_path
        else:
            logger.debug(f"{root_path} is an unsupported file")
            return
    else:
        logger.debug(f"{root_path} is a directory, scanning folders recursively...")
        for path in sorted(root_path.rglob("*")):
            if path.is_file():
                if is_supported(path):
                    logger.debug(f"{path} is a supported file")
                    yield path
                else:
                    logger.debug(f"{path} is an unsupported file")
