import datetime
from pathlib import Path
from typing import Optional

import click

from gpy import config
from gpy.exiftool import client as exiftool
from gpy.exiftool.client import ExifToolError
from gpy.filenames import parse_datetime
from gpy.filesystem import get_paths_recursive
from gpy.log import log


@click.group(name="meta")
def meta_group() -> None:
    """Edit file metadata."""
    pass


@meta_group.command(name="date")
# @click.option('--clean-all', is_flag=True, default=False, help='remove all metadata')
@click.option(
    "--backup",
    is_flag=True,
    default=False,
    help="keep a backup copy of the edited file",
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
    backup: bool,
) -> None:
    """Edit file metadata date and time."""
    meta_date = None
    if input and from_filename:
        log(
            "ORDER CONFLICT. Which date should I use? The date you've input or "
            "the file name one?"
        )
        return
    if input:
        # TODO: unify date parsers!
        input_date = input_to_datetime(input)
        if input_date and not input_date.tzinfo:
            meta_date = set_timezone_to_default(input_date)
        else:
            meta_date = input_date

    for file_path in get_paths_recursive(root_path=Path(path)):
        if not input and from_filename:
            filename_date = parse_datetime(file_path.name)
            if filename_date and not filename_date.tzinfo:
                filename_date = set_timezone_to_default(filename_date)
            meta_date = filename_date
        if meta_date:
            edit_date(file_path, meta_date, backup)


def set_timezone_to_default(ts: datetime.datetime) -> datetime.datetime:
    return datetime.datetime.combine(
        ts.date(),
        ts.time(),
        tzinfo=config.DEFAULT_ZONEINFO,
    )


def edit_date(file_path: Path, ts: datetime.datetime, backup: bool) -> None:
    """Write date and time to file metadata."""
    formatted_date = ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    log(f"writing date {formatted_date} as metadata to {file_path}", fg="bright_black")
    try:
        exiftool.write_ts(file_path, ts=ts, backup=backup)
    except ExifToolError as exc:
        log(exc.args[0])


def input_to_datetime(input: str) -> datetime.datetime:
    """Try to parse input string to a datetime.datetime object.

    If unsuccessful, log a meaningful message.
    """
    for fmt in ("%Y-%m-%d_%H:%M:%S", "%Y-%m-%d_%H:%M:%S.%f"):
        try:
            return datetime.datetime.strptime(input, fmt)
        except Exception:
            pass

    msg = "ERROR: provided input doesn't have the required format (YYYY-MM-DD_hh:mm:ss.ms)"
    raise Exception(msg)
