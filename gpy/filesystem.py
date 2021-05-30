import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterator, List, Tuple

from gpy.google_sheet import FileReport
from gpy.types import (
    FileDateReport,
    FileReportFromTable,
    JsonDict,
    structure,
    unstructure,
)

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


ColumnCoordinates = Tuple[int, int]
Dimensions = Dict[str, ColumnCoordinates]


def get_table_dimensions(headers: List[str], split: str) -> Dimensions:
    # headers: list of header names
    # split: bunch of lines that splits headers and lines in the table and have the size
    #        of each column
    columns = split.split("  ")
    dimensions: Dimensions = {}
    cursor = 0
    for header, column in zip(headers, columns):
        column_start = cursor
        column_width = len(column)

        # this sets the cursor in the first character of the gap between columns
        cursor += column_width

        column_end = cursor - 1

        column_coordinates = (column_start, column_end)
        dimensions[header] = column_coordinates

        # this sets the cursor in the first character of the next column
        cursor += 2

    return dimensions


ParsedLine = Dict[str, Any]


def split_line_by_dimensions(raw_line: str, dimensions: Dimensions) -> ParsedLine:
    line: ParsedLine = {}
    for header, column_coordinates in dimensions.items():
        column_start, column_end = column_coordinates
        raw_value = raw_line[column_start : column_end + 1]
        line[header] = raw_value.strip()
    return line


def read_table(path: Path) -> List[FileReportFromTable]:
    assert path.exists(), f"File {path} does not exit"

    raw = path.read_text()
    raw_lines = iter(raw.split("\n"))
    raw_headers = next(raw_lines)

    def _parse_headers(raw: str) -> List[str]:
        parsed_headers = [chunk.strip() for chunk in raw.split("  ") if chunk]
        return parsed_headers

    headers = _parse_headers(raw_headers)

    header_and_body_separator = next(raw_lines)  # separator between header and body

    table_dimensions = get_table_dimensions(headers, header_and_body_separator)

    def _parse_line(raw: str) -> ParsedLine:
        line_with_raw_values = split_line_by_dimensions(raw, table_dimensions)
        line: ParsedLine = {}
        # Pre parse empty strings and booleans where you don't want cattrs default
        # behaviour. Cattrs default behaviour should not change, as you are using it
        # in other places
        for header, raw_value in line_with_raw_values.items():
            if raw_value == "":
                line[header] = None
            elif raw_value == "True":
                line[header] = True
            elif raw_value == "False":
                line[header] = False
            else:
                line[header] = raw_value

        return line

    def _line_to_file_report(line: ParsedLine) -> FileReportFromTable:
        report = structure(line, FileReportFromTable)
        return report

    raw_table = map(_parse_line, raw_lines)
    table = list(map(_line_to_file_report, raw_table))

    return table


def save_table(path: Path, data: str) -> None:
    if path.exists():
        path.unlink()

    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(data)
