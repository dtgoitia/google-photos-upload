import datetime
from pathlib import Path
from typing import Optional

import click

from gpy import exiftool
from gpy.filesystem import get_paths_recursive
from gpy.parsers.dates import try_to_parse_date
from gpy.parsers.filenames import parse
from gpy.types import Report


@click.group()
def main():
    """Entry point."""
    pass


@main.group()
def scan():
    """Scan file and directory metadata."""
    pass


@main.group()
def meta():
    """Edit file metadata."""
    pass


@scan.command(name="date")
@click.argument("path", type=click.Path(exists=True))
def gyp_scan_date(path):
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


@meta.command(name="date")
# @click.option('--clean-all', is_flag=True, default=False, help='remove all metadata')
@click.option(
    "--no-backup",
    is_flag=True,
    default=False,
    help="do not keep a backup copy of the edited file",
)
# @click.option('--timezone', default=0, help='')  # TODO
@click.option(
    "--from-filename",
    is_flag=True,
    default=False,
    help="write file name date to metadata",
)
@click.option("--input", help="manually input date and time (YYYY-MM-DD_hh:mm:ss.ms)")
@click.argument("path", type=click.Path(exists=True))
# def date(clean_all, no_backup, from_filename, path):
def cmd_meta_date(
    path: str,
    from_filename: bool,
    input: Optional[str],
    no_backup: bool,
) -> None:
    """Edit file metadata date and time."""
    meta_date = None
    if input and from_filename:
        log(
            "ORDER CONFLICT. Which date should I use? The date you've input or the file name one?"
        )
        return
    if input:
        meta_date = input_to_datetime(input)

    for file_path in get_paths_recursive(root_path=Path(path)):
        if input is None and from_filename:
            filename_date = parse(file_path.name)
            meta_date = filename_date
        if meta_date:
            edit_date(file_path, meta_date, no_backup)


def scan_date(file_path: Path) -> Report:
    """Scan file date and time metadata."""
    log(f"scanning {file_path}", fg="bright_black")

    filename_date = parse(file_path.name)
    metadata_date_string = exiftool.read_datetime(file_path)
    metadata_date = try_to_parse_date(metadata_date_string)

    return Report(
        path=file_path,
        filename_date=filename_date,
        metadata_date=metadata_date,
    )


def scan_gps(file_path: Path) -> Report:
    """Scan file geolocation related metadata."""
    log(f"scanning {file_path}", fg="bright_black")
    gps = exiftool.read_gps(file_path)
    return Report(path=file_path, gps=gps)


def edit_date(file_path: Path, ts: datetime.datetime, no_backup: bool) -> None:
    """Write date and time to file metadata."""
    formatted_date = ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    log(f"writing date {formatted_date} as metadata to {file_path}", fg="bright_black")
    file_is_updated = exiftool.write_datetime(file_path, ts=ts, no_backup=no_backup)
    if not file_is_updated:
        log("IT WAS NOT POSSIBLE")


def input_to_datetime(input: str) -> Optional[datetime.datetime]:
    """Try to parse input string to a datetime.datetime object.

    If unsuccessful, log a meaningful message.
    """
    for fmt in ("%Y-%m-%d_%H:%M:%S", "%Y-%m-%d_%H:%M:%S.%f"):
        try:
            return datetime.datetime.strptime(input, fmt)
        except Exception:
            pass
    log(
        "ERROR: provided input doesn't have the required format (YYYY-MM-DD_hh:mm:ss.ms)"
    )
    return None


def print_report(report: Report) -> None:
    """Print on screen a report dictionary."""
    if not report.dates_match:
        log("    metadata date and file timestamp don't match")


def log(s: str, fg: Optional[str] = None) -> None:
    """Log with colour."""
    click.echo(click.style(s, fg=fg))


# TODO:
# Add more regex patterns to recognize more image file names and ensure the date
# Create one command that will:
#   1. Scan all images or videos in the directory
#   2. Try to parse the filename to extract timestamp.
#   3. Look data and geolocation metadata in the files.
#   4. Report:
#        - Filename and metadata match, +GPS -> OK
#        - If no GPS metadata -> Add '_nogps' at the end of the filename
#        - Filename and metadata don't match ->
