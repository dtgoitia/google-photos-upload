import click
import gpy.exiftool as exif
import os


@click.group()
def main():
    """Entry point."""
    pass


@main.command()
@click.option('--clean-all', is_flag=True, default=False, help='remove all metadata')
@click.option('--no-backup', is_flag=True, default=False, help='do not keep a backup copy of the edited file')
@click.option('--parse-date', is_flag=True, default=False, help='write date to metadata from file name')
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


@main.command()
@click.argument('path', type=click.Path(exists=True))
def scan(path):
    """Scan files and directories.

    Scan files and directories looking and report:
     - Supported files: the metadata of these files can be manipulated.
     - Date tag: the supported file does/doesn't have date tag.
     - GPS tag: the supported file does/doesn't have GPS tag.
    """
    scan_recursive(path)


def scan_recursive(path):
    """Recursivelly scan files and directories."""
    if os.path.isdir(path):
        log(f'directory found {path}...', fg='bright_black')
        paths = [os.path.join(path, x) for x in os.listdir(path)]
        [scan_recursive(p) for p in paths]
        return
    file_path = path
    log(f'scanning {file_path}', fg='bright_black')
    report = {'path': file_path}
    date = exif.read_datetime(file_path)
    gps = exif.read_gps(file_path)
    if date is not None:
        report['date'] = date
    if gps is not None:
        report['gps'] = gps
    report_scan(report)


def report_scan(report: dict) -> None:
    """Print on screen a report dictionary."""
    result = report['path']
    if report.get('date'):
        result += f"  date={report['date']}"
    if report.get('gps'):
        result += f"  gps={report['gps']}"
    log(result)


def log(s: str, fg=None):
    """Log with colour."""
    click.echo(click.style(s, fg=fg))
