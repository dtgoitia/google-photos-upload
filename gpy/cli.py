import click
import datetime
from gpy import exiftool
from gpy.filenames import parse
import os
import re
from typing import Any, Dict, Iterable, Optional


DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


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


@scan.command(name='date')
@click.argument('path', type=click.Path(exists=True))
def gyp_scan_date(path):
    """Scan files and directories.

    Scan files and directories looking and report:
     - Supported files: the metadata of these files can be manipulated.
     - Date tag: the supported file does/doesn't have date tag.
     - GPS tag: the supported file does/doesn't have GPS tag.
    """
    file_paths = get_paths_recursive(root_path=path)
    for file_path in file_paths:
        report = scan_date(file_path)
        print_report(report)


@meta.command(name='date')
# @click.option('--clean-all', is_flag=True, default=False, help='remove all metadata')
# @click.option('--no-backup', is_flag=True, default=False, help='do not keep a backup copy of the edited file')
@click.option('--from-filename', is_flag=True, default=False, help='write date to metadata from file name')
@click.option('--input', help='manually input date and time (YYYY-MM-DD hh:mm:ss)')
@click.argument('path', type=click.Path(exists=True))
# def date(clean_all, no_backup, from_filename, path):
def cmd_meta_date(from_filename: bool, path: str, input: Optional[str]):
    """Edit file metadata date and time."""
    file_paths = get_paths_recursive(root_path=path)
    meta_date = None
    if input and from_filename:
        log("ORDER CONFLICT. Which date should I use? The date you've input or the file name one?")
        return
    if input:
        meta_date = input_to_datetime(input)

    for file_path in file_paths:
        if input is None and from_filename:
            filename_date = parse(os.path.basename(file_path))
            meta_date = filename_date
        if meta_date:
            edit_date(file_path, meta_date)


def scan_date(file_path: str) -> Dict[str, Any]:
    """Scan file date and time metadata."""
    log(f'scanning {file_path}', fg='bright_black')
    report = {'path': file_path}  # type: Dict[str, Any]
    filename_date = parse(os.path.basename(file_path))
    metadata_date_string = exiftool.read_datetime(file_path)
    metadata_date = try_to_parse_date(metadata_date_string)
    report['filename_date'] = filename_date
    report['metadata_date'] = metadata_date
    report['match_date'] = compare_dates(filename_date, metadata_date)
    return report


def try_to_parse_date(text: Optional[str]) -> Optional[datetime.datetime]:
    """Parse the date with multiple formats and return the first match."""
    if not text:
        return None
    case_1 = try_to_parse_date_1(text)
    if case_1:
        return case_1
    case_2 = try_to_parse_date_2(text)
    if case_2:
        return case_2
    return None


def try_to_parse_date_1(text: str) -> Optional[datetime.datetime]:
    """Try to parse text to date (2019-02-02 18:45:13)."""
    pattern = r'([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2})'
    matches = re.match(pattern, text)
    if matches is None:
        return None
    year = int(matches.group(1))
    month = int(matches.group(2))
    day = int(matches.group(3))
    h = int(matches.group(4))
    m = int(matches.group(5))
    s = int(matches.group(6))
    return datetime.datetime(year, month, day, h, m, s)


def try_to_parse_date_2(text: str) -> Optional[datetime.datetime]:
    """Try to parse text to date (2019-02-02 18:45:13.00+00:00)."""
    pattern = r'([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2}).[0-9]{2}\+[0-9]{2}:[0-9]{2}'
    matches = re.match(pattern, text)
    if matches is None:
        return None
    year = int(matches.group(1))
    month = int(matches.group(2))
    day = int(matches.group(3))
    h = int(matches.group(4))
    m = int(matches.group(5))
    s = int(matches.group(6))
    return datetime.datetime(year, month, day, h, m, s)


def scan_gps(file_path) -> dict:
    """Scan file geolocation related metadata."""
    log(f'scanning {file_path}', fg='bright_black')
    report = {'path': file_path}
    gps = exiftool.read_gps(file_path)
    if gps is not None:
        report['gps'] = gps
    return report


def compare_dates(a: Optional[datetime.datetime], b: Optional[datetime.datetime]) -> bool:
    """Check wheather the datetimes are the same or not.

    This function returns False if any of the datetimes is None.
    """
    if (a is None) or (b is None):
        return False
    if a == b:
        return True
    return False


def edit_date(file_path: str, ts: datetime.datetime):
    """Write date and time to file metadata."""
    formatted_date = ts.strftime(DATETIME_FORMAT)
    log(f'writing date {formatted_date} as metadata to {file_path}', fg='bright_black')
    file_is_updated = exiftool.write_datetime(file_path, ts=ts)
    if not file_is_updated:
        log('IT WAS NOT POSSIBLE')


def input_to_datetime(input: str) -> Optional[datetime.datetime]:
    """Try to parse input string to a datetime.datetime object.

    If unsuccessful, log a meaningful message.
    """
    try:
        return datetime.datetime.strptime(input, DATETIME_FORMAT)
    except Exception:
        log(f"ERROR: provided input doesn't have the required format ()")
        return None


def is_supported(file_path: str) -> bool:
    """Return true if the file is supported.

    At the moment only the following extensions are supported:
        - .jpg
        - .png
        - .mp4
        - .3gp
    """
    filename, file_extension = os.path.splitext(file_path)
    supported_extensions = ('.jpg', '.png', '.mp4', '.3gp')
    if file_extension in supported_extensions:
        return True
    return False


def get_paths_recursive(*, root_path) -> Iterable[str]:
    """Yield absolute path of supported files under root_path.

    Refer to is_supported() for further information on supported files.
    """
    is_file = True
    paths = os.walk(root_path)
    for path, dirs, files in paths:
        is_file = False
        for file in files:
            absolute_path = os.path.abspath(os.path.join(path, file))
            if is_supported(absolute_path):
                yield absolute_path
    if is_file:
        yield root_path


def print_report(report: dict) -> None:
    """Print on screen a report dictionary."""
    match = report['match_date']
    if match is False:
        log(f"    metadata date and file timestamp don't match")


def log(s: str, fg=None):
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
