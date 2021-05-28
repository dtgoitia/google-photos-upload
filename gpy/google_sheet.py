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
    gphotos_compatible_metadata: Optional[datetime.datetime]
    ready_to_upload: bool
    uploaded: bool
    add_google_timestamp: bool
    convert_to_mp4: bool
    upload_in_next_reconcile: bool

    def to_gsheet(self) -> List[Union[str, bool]]:
        if self.filename_date:
            filename_date = self.filename_date.isoformat()
        else:
            filename_date = EMPTY_CELL

        if self.metadata_date:
            metadata_date = self.metadata_date.isoformat()
        else:
            metadata_date = EMPTY_CELL

        if self.gphotos_compatible_metadata:
            gphotos_compatible_metadata = self.gphotos_compatible_metadata.isoformat()
        else:
            gphotos_compatible_metadata = EMPTY_CELL

        # if self.uploaded is None:
        #     uploaded = EMPTY_CELL
        # else:
        #     uploaded = self.uploaded

        # if self.upload_in_next_reconcile is None:
        #     upload_in_next_reconcile = EMPTY_CELL
        # else:
        #     upload_in_next_reconcile = self.upload_in_next_reconcile

        file_type = self.path.suffix

        # Order matters!
        return [
            self.file_id,
            str(self.path),
            self.path.name,
            filename_date,
            metadata_date,
            self.dates_match,
            gphotos_compatible_metadata,
            self.ready_to_upload,
            self.uploaded,
            self.add_google_timestamp,
            self.convert_to_mp4,
            self.upload_in_next_reconcile,
            file_type,
        ]


Worksheet = Dict[FileId, GSheetRow]


@attr.s(auto_attribs=True, frozen=True)
class FileReport:
    """Current status of a file, both in terms of metadata and being uploaded."""

    file_id: FileId
    path: Path
    filename_date: Optional[datetime.datetime]
    metadata_date: Optional[datetime.datetime]
    dates_match: bool
    gphotos_compatible_metadata: Optional[datetime.datetime]
    ready_to_upload: bool
    uploaded: bool
    add_google_timestamp: bool
    convert_to_mp4: bool
    upload_in_next_reconcile: bool

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
            add_google_timestamp=self.add_google_timestamp,
            convert_to_mp4=self.convert_to_mp4,
            upload_in_next_reconcile=self.upload_in_next_reconcile,
        )


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
            gphotos_compatible_metadata=cast_datetime(
                row["gphotos_compatible_metadata"]
            ),
            ready_to_upload=cast_bool(row["ready_to_upload"]),
            uploaded=cast_bool(row["uploaded"]),
            add_google_timestamp=cast_bool(row["add_google_timestamp"]),
            convert_to_mp4=cast_bool(row["convert_to_mp4"]),
            upload_in_next_reconcile=cast_bool(row["upload_in_next_reconcile"]),
        )

        gsheet[gsheet_row.file_id] = gsheet_row

    return gsheet


def merge(gsheet: Worksheet, reports: List[FileReport]) -> Worksheet:
    merged = copy.copy(gsheet)

    for file_report in reports:
        merged[file_report.file_id] = file_report.to_gsheet_row()

    return merged


def column_index_to_name(index: int) -> str:
    """Map the column index to its name in GSheet."""
    return [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
    ][index - 1]


def upload_worksheet(sh: Spreadsheet, gsheet: Worksheet) -> None:
    sorted_rows = sorted([v for v in gsheet.values()], key=lambda v: v.file_id)

    values = [row.to_gsheet() for row in sorted_rows]

    any_row_values = values[0]
    last_row_index = len(gsheet) + 1
    last_column_name = column_index_to_name(index=len(any_row_values))
    range = f"A2:{last_column_name}{last_row_index}"

    sh.get_worksheet(1).update(range, values)
