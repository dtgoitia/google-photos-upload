import json
import logging
from pathlib import Path
from typing import Iterator, List

from gpy.google_sheet import FileReport
from gpy.types import FileDateReport, JsonDict, structure, unstructure

logger = logging.getLogger(__name__)


def is_supported(path: Path) -> bool:
    return path.suffix.lower() in (".jpg", ".png", ".mp4", ".3gp", ".avi")


def is_video(path: Path) -> bool:
    return path.suffix.lower() in (".mp4", ".3gp", ".avi")


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

        files_and_dirs = sorted(root_path.rglob("*"))
        files = (path for path in files_and_dirs if path.is_file())

        for path in files:
            if not is_supported(path):
                logger.debug(f"{path} is an unsupported file")
                continue

            logger.debug(f"{path} is a supported file")
            yield path


def create_parent_folder_if_required(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> JsonDict:
    with path.open("r") as f:
        return json.load(f)


def write_json(path: Path, content: JsonDict) -> None:
    create_parent_folder_if_required(path)
    with path.open("w") as f:
        json.dump(content, f, indent=2)


def read_reports(path: Path) -> List[FileDateReport]:
    data = read_json(path)
    reports = structure(data, List[FileDateReport])
    return reports


def write_reports(path: Path, reports: List[FileDateReport]) -> None:
    create_parent_folder_if_required(path)
    content = unstructure(reports)

    logger.info(f"Writing report to {path}")
    write_json(path=path, content=content)


def read_aggregated_reports(path: Path) -> List[FileReport]:
    data = read_json(path)
    reports = structure(data, List[FileReport])
    return reports
