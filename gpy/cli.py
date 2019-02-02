import click
import datetime
import gpy.exiftool as exif
import os
from gpy.filenames import parse
from typing import Any, Dict, Iterable, Optional


@click.group()
def main():
    """Entry point."""
    pass


@main.group()
def scan():
    """Scan file and directory metadata."""
    pass


@scan.command()
@click.argument('path', type=click.Path(exists=True))
def date(path):
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


def scan_date(file_path) -> Dict[str, Any]:
    """Scan file date and time metadata."""
    log(f'scanning {file_path}', fg='bright_black')
    report = {'path': file_path}
    metadata_date = exif.read_datetime(file_path)
    filename_date = parse(os.path.basename(file_path))
    ts = None
    try:
        ts = datetime.datetime.strptime(metadata_date, '%Y-%m-%d %H:%M:%S')  # type: ignore
        report['metadata_date'] = ts
    except Exception:
        report['metadata_date'] = None
    report['filename_date'] = filename_date
    report['match_date'] = compare_dates(filename_date, ts)
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


def scan_gps(file_path) -> dict:
    """Scan file geolocation related metadata."""
    log(f'scanning {file_path}', fg='bright_black')
    report = {'path': file_path}
    gps = exif.read_gps(file_path)
    if gps is not None:
        report['gps'] = gps
    return report


def print_report(report: dict) -> None:
    """Print on screen a report dictionary."""
    match = report['match_date']
    if match is False:
        log(f"    metadata date and file timestamp don't match")
    pass


def log(s: str, fg=None):
    """Log with colour."""
    click.echo(click.style(s, fg=fg))


@main.command()
@click.option('--clean-all', is_flag=True, default=False, help='remove all metadata')
@click.option('--no-backup', is_flag=True, default=False, help='do not keep a backup copy of the edited file')
@click.option('--parse-filename', is_flag=True, default=False, help='write date to metadata from file name')
@click.argument('path', type=click.Path(exists=True))
def meta(clean_all, no_backup, parse_date, path):
    """Read and write file metadata."""
    meta_recursive(clean_all, no_backup, parse_date, path)
    # TODO: add option to scan directory and return a list of filenames which are missing either GPS or dates


def meta_recursive(clean_all, no_backup, parse_date, path):
    """Recursivelly manage metadata in directories and files."""
    if os.path.isdir(path):
        log(f'directory found {path}...', fg='bright_black')
        paths = [os.path.join(path, x) for x in os.listdir(path)]
        [meta_recursive(clean_all, no_backup, parse_date, p) for p in paths]
        return
    file_path = path
    log(f'processing {file_path}', fg='bright_black')
    if clean_all:
        log(f"Removing all metadata from '{file_path}' file...", fg='bright_black')
        exif.clean_metadata(file_path, no_backup=no_backup)
    if parse_date:
        log(f"Extracting date and time from '{file_path}' file name...", fg='bright_black')
        date = exif.parse_date_from_filename(file_path)
        log(f"Writing dateTime tag to '{file_path}' file...", fg='bright_black')
        exif.write_datetime(file_path, ts=date, no_backup=no_backup)

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


if __name__ == "__main__":
    main(['scan', 'date', '.'])
