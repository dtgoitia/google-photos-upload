import copy
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import attr
from gspread.models import Spreadsheet

from gpy.types import FileId

EMPTY_CELL = ""

# @attr.s(auto_attribs=True, frozen=True)
# class Album:
#     id: str
#     name: str


@attr.s(auto_attribs=True, frozen=True)
class GSheetRow:
    file_id: FileId
    path: Path
    filename_date: Optional[datetime.datetime]
    metadata_date: datetime.datetime
    dates_match: bool
    gphotos_compatible_metadata: bool
    ready_to_upload: bool
    uploaded: Optional[bool] = None
    upload_in_next_reconcile: Optional[bool] = None

    def to_gsheet(self) -> List[Union[str, bool]]:
        if self.filename_date:
            filename_date = self.filename_date.isoformat()
        else:
            filename_date = EMPTY_CELL

        if self.metadata_date:
            metadata_date = self.metadata_date.isoformat()
        else:
            metadata_date = EMPTY_CELL

        if self.uploaded is None:
            uploaded = EMPTY_CELL
        else:
            uploaded = self.uploaded

        if self.upload_in_next_reconcile is None:
            upload_in_next_reconcile = EMPTY_CELL
        else:
            upload_in_next_reconcile = self.upload_in_next_reconcile

        return [
            self.file_id,
            str(self.path),
            self.path.name,
            filename_date,
            metadata_date,
            self.dates_match,
            self.gphotos_compatible_metadata,
            self.ready_to_upload,
            uploaded,
            upload_in_next_reconcile,
        ]


Worksheet = Dict[FileId, GSheetRow]


@attr.s(auto_attribs=True, frozen=True)
class FileReport:
    """Current status of a file, both in terms of metadata and being uploaded."""

    file_id: FileId
    path: Path
    filename_date: Optional[datetime.datetime]
    metadata_date: datetime.datetime
    dates_match: bool
    gphotos_compatible_metadata: bool
    ready_to_upload: bool
    uploaded: bool

    def to_gsheet_row(self) -> GSheetRow:
        return GSheetRow(
            file_id=self.file_id,
            path=self.path,
            filename_date=self.filename_date,
            metadata_date=self.metadata_date,
            dates_match=self.dates_match,
            gphotos_compatible_metadata=self.gphotos_compatible_metadata,
            ready_to_upload=self.ready_to_upload,
            uploaded=self.uploaded,
            upload_in_next_reconcile=None,  # TODO: add support for this
        )


Report = List[FileReport]


def cast_datetime(s: str) -> Optional[datetime.datetime]:
    if s == EMPTY_CELL:
        return None

    return datetime.datetime.fromisoformat(s)


def cast_bool(s: str) -> Optional[bool]:
    if s == "TRUE":
        return True

    if s == "FALSE":
        return False

    if s == EMPTY_CELL:
        return None

    raise ValueError(f"String {s!r} cannot be converted to a boolean")


def fetch_worksheet(sh: Spreadsheet) -> Worksheet:
    raw_sheet = sh.get_worksheet(1).get_all_records()

    gsheet: Worksheet = {}

    for row in raw_sheet:
        # album = None
        # album_id = row["albumId"]
        # album_name = row["albumName"]
        # if album_id and album_name:
        #     album = Album(id=album_id, name=album_name)

        gsheet_row = GSheetRow(
            file_id=row["file_id"],
            path=Path(row["path"]),
            filename_date=cast_datetime(row["filename_date"]),
            metadata_date=cast_datetime(row["metadata_date"]),
            dates_match=cast_bool(row["dates_match"]),
            gphotos_compatible_metadata=cast_bool(row["gphotos_compatible_metadata"]),
            ready_to_upload=cast_bool(row["ready_to_upload"]),
            uploaded=cast_bool(row["uploaded"]),
            upload_in_next_reconcile=cast_bool(row["upload_in_next_reconcile"]),
        )

        gsheet[gsheet_row.file_id] = gsheet_row

    return gsheet


def merge(gsheet: Worksheet, report: Report) -> Worksheet:
    merged = copy.copy(gsheet)

    for file in report:
        merged[file.file_id] = file.to_gsheet_row()

    return merged


def upload_worksheet(sh: Spreadsheet, gsheet: Worksheet) -> None:
    last_row = len(gsheet) + 1
    range = f"A2:J{last_row}"

    sorted_rows = sorted([v for v in gsheet.values()], key=lambda v: v.file_id)

    values = [row.to_gsheet() for row in sorted_rows]

    sh.get_worksheet(1).update(range, values)
