import datetime
from pathlib import Path
from typing import Optional

import click

from gpy import exiftool
from gpy.filesystem import get_paths_recursive
from gpy.log import log
from gpy.parsers.filenames import parse


@click.group(name="meta")
def meta_group() -> None:
    """Edit file metadata."""
    pass


@meta_group.command(name="date")
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
def meta_date_command(
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
