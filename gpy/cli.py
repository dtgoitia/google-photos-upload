import click
import gpy.exiftool as exif
import os


@click.group()
def main():
    """Entry point."""
    # click.echo('main')
    pass


@main.command()
@click.option('--clean-all', is_flag=True, default=False, help='remove all metadata')
@click.option('--parse-date', is_flag=True, default=False, help='write date to metadata from file name')
@click.option('--no-backup', is_flag=True, default=False, help='do not keep a backup copy of the edited file')
@click.argument('path', type=click.Path(exists=True))
def meta(clean_all, parse_date, overwrite_original, path):
    """Read and write file metadata."""
    meta_recursive(clean_all, parse_date, overwrite_original, path)
    # TODO: add option to scan directory and return a list of filenames which are missing either GPS or dates


def meta_recursive(clean_all, parse_date, overwrite_original, path, ):
    """Recursivelly manage metadata in directories and files."""
    if os.path.isdir(path):
        log(f'Directory found {path}...', fg='bright_black')
        paths = [os.path.join(path, x) for x in os.listdir(path)]
        [meta_recursive(clean_all, parse_date, p) for p in paths]
        return
    file_path = path
    log(f'processing {file_path}', fg='bright_black')
    if clean_all:
        log(f"Removing all metadata from '{file_path}' file...", fg='bright_black')
        exif.clean_metadata(file_path)
    if parse_date:
        log(f"Extracting date and time from '{file_path}' file name...", fg='bright_black')
        date = exif.parse_date_from_filename(file_path)
        log(f"Writing dateTime tag to '{file_path}' file...", fg='bright_black')
        exif.write_datetime(file_path, ts=date)


def log(s: str, fg=None):
    """Log with colour."""
    click.echo(click.style(s, fg=fg))
