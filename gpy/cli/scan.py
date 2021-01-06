from pathlib import Path

import click

from gpy import exiftool
from gpy.filesystem import get_paths_recursive
from gpy.log import log, print_report
from gpy.parsers.filenames import get_datetime_from_filename
from gpy.types import Report


@click.group(name="scan")
def scan_group() -> None:
    """Scan file and directory metadata."""
    pass


@scan_group.command(name="date")
@click.argument("path", type=click.Path(exists=True))
def scan_date_command(path):
    """Scan files and directories.

    Scan files and directories looking and report:
     - Supported files: the metadata of these files can be manipulated.
     - Date tag: the supported file does/doesn't have date tag.
     - GPS tag: the supported file does/doesn't have GPS tag.
    """
    file_paths = get_paths_recursive(root_path=Path(path))
    for file_path in file_paths:
        report = scan_date(file_path)
        print_report(report)


def scan_date(path: Path) -> Report:
    """Scan file date and time metadata."""
    log(f"scanning {path}", fg="bright_black")

    filename_date = get_datetime_from_filename(path.name)
    metadata_date = exiftool.read_datetime(path)

    return Report(
        path=path,
        filename_date=filename_date,
        metadata_date=metadata_date,
    )


def scan_gps(file_path: Path) -> Report:
    """Scan file geolocation related metadata."""
    log(f"scanning {file_path}", fg="bright_black")
    gps = exiftool.read_gps(file_path)
    return Report(path=file_path, gps=gps)
