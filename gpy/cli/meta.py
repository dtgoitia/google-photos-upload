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


@meta_group.command(name="date", help="Edit file metadata date and time.")
# @click.option('--clean-all', is_flag=True, default=False, help='remove all metadata')
@click.option(
    "--backup",
    is_flag=True,
    default=False,
    help="keep a backup copy of the edited file",
)
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
    edit_metadata_datetime(
        path=Path(path),
        read_datetime_from_filename=from_filename,
        input=input,
        backup=backup,
    )


def edit_metadata_datetime(
    path: Path,
    read_datetime_from_filename: bool,
    input: Optional[str],
    backup: bool,
) -> None:
    metadata_datetime: Optional[datetime.datetime] = None

    if input and read_datetime_from_filename:
        log(
            "COMMAND OPTION CONFLICT. "
            "Please specify either --input or --from-filename, but not both"
        )
        return

    if input:
        input_datetime = input_to_datetime(input)
        if input_datetime and not input_datetime.tzinfo:
            input_datetime = set_timezone_to_default(input_datetime)
        metadata_datetime = input_datetime

    for path in get_paths_recursive(root_path=Path(path)):
        if read_datetime_from_filename:
            filename_date = parse_datetime(path.name)
            if filename_date and not filename_date.tzinfo:
                filename_date = set_timezone_to_default(filename_date)
            metadata_datetime = filename_date

        assert metadata_datetime
        formatted_date = metadata_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log(
            f"writing date {formatted_date} as metadata to {path}",
            fg="bright_black",
        )
        try:
            exiftool.write_ts(path, ts=metadata_datetime, backup=backup)
        except ExifToolError as exc:
            log(exc.args[0])


def set_timezone_to_default(ts: datetime.datetime) -> datetime.datetime:
    return datetime.datetime.combine(
        ts.date(),
        ts.time(),
        tzinfo=config.DEFAULT_ZONEINFO,
    )


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
