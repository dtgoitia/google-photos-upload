import logging
from pathlib import Path
from typing import Any, List, Optional  # TODO: find namespace type

import click

from gpy.exiftool import client as exiftool_client
from gpy.filenames import DatetimeParser
from gpy.filenames import parse_datetime as datetime_parser
from gpy.filesystem import get_paths_recursive, write_reports
from gpy.types import Report, print_report

logger = logging.getLogger(__name__)


@click.group(name="scan")
def scan_group() -> None:
    """Scan file and directory metadata."""
    pass


@scan_group.command(name="date")
@click.option("--report", "report_output", type=click.Path())
@click.argument("path", type=click.Path(exists=True))
def scan_date_command(report_output: Optional[str], path: str) -> None:
    """Scan files and directories.

    Scan files and directories looking and report:
     - Supported files: the metadata of these files can be manipulated.
     - Date tag: the supported file does/doesn't have date tag.
     - GPS tag: the supported file does/doesn't have GPS tag.
    """
    reports = scan_date(exiftool_client, datetime_parser, Path(path))

    if report_output:
        report_path = Path(report_output)
        write_reports(path=report_path, reports=reports)


def scan_date(exiftool: Any, parse_datetime: DatetimeParser, dir: Path) -> List[Report]:
    file_paths = get_paths_recursive(root_path=Path(dir))

    return [_scan_date(exiftool, parse_datetime, path) for path in file_paths]


def _scan_date(exiftool: Any, parse_datetime: DatetimeParser, path: Path) -> Report:
    logger.info(f"scanning {path}")

    filename_date = parse_datetime(path.name)
    metadata_date = exiftool.read_datetime(path)
    google_date = exiftool.read_google_timestamp(path)
    logger.debug("scan successfully completed")

    logger.debug("reporting scanned dates...")
    report = Report(
        path=path,
        filename_date=filename_date,
        metadata_date=metadata_date,
        google_date=google_date,
    )
    print_report(report)

    return report


def scan_gps(exiftool: Any, file_path: Path) -> Report:
    logger.info(f"scanning {file_path}")
    gps = exiftool.read_gps(file_path)
    return Report(path=file_path, gps=gps)
