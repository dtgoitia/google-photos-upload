import copy
from pathlib import Path
from typing import Dict, List, Optional, Union

import attr
from gspread.models import Spreadsheet


@attr.s(auto_attribs=True, frozen=True)
class Album:
    id: str
    name: str


@attr.s(auto_attribs=True, frozen=True)
class GSheetRow:
    id: str
    last_filename: str
    last_dir: str
    dates_match: bool
    has_ghotos_timestamp: bool
    uploaded: bool
    album: Optional[Album] = None

    def to_gsheet(self) -> List[Union[str, bool]]:
        return [
            self.id,
            self.last_filename,
            self.last_dir,
            self.dates_match,
            self.has_ghotos_timestamp,
            self.uploaded,
            "",  # TODO: support album ID
            "",  # TODO: support album name
        ]


GSheet = Dict[str, GSheetRow]


def cast_bool(s: str) -> bool:
    if s == "TRUE":
        return True

    if s == "FALSE":
        return False

    raise ValueError(f"String {s!r} cannot be converted to a boolean")


def fetch_worksheet(sh: Spreadsheet) -> GSheet:
    raw_sh = sh.sheet1.get_all_records()

    gsheet: GSheet = {}

    for row in raw_sh:
        album = None
        album_id = row["albumId"]
        album_name = row["albumName"]
        if album_id and album_name:
            album = Album(id=album_id, name=album_name)

        gsheet_row = GSheetRow(
            id=row["ID"],
            last_filename=row["Last filename"],
            last_dir=row["Last dir"],
            dates_match=cast_bool(row["Filename and metadata dates do match"]),
            has_ghotos_timestamp=cast_bool(row["has GPhotos timestamp"]),
            uploaded=cast_bool(row["uploaded"]),
            album=album,
        )

        gsheet[gsheet_row.id] = gsheet_row

    return gsheet


@attr.s(auto_attribs=True, frozen=True)
class FileReport:
    path: Path
    dates_match: bool
    has_ghotos_timestamp: bool
    uploaded: bool

    @property
    def id(self) -> str:
        return str(self.path)

    def to_gsheet_row(self) -> GSheetRow:
        return GSheetRow(
            id=self.id,
            last_filename=self.path.name,
            last_dir=str(self.path.parent),
            dates_match=self.dates_match,
            has_ghotos_timestamp=self.has_ghotos_timestamp,
            uploaded=self.uploaded,
            album=None,  # TODO: think how to figure albums out
        )


Report = List[FileReport]


def merge(gsheet: GSheet, report: Report) -> GSheet:
    merged = copy.copy(gsheet)

    for file in report:
        # TODO: consider if cherry-picking row attributes is worth, instead of
        # just overwriting all the attributes
        merged[file.id] = file.to_gsheet_row()

    return merged


def upload_worksheet(sh: Spreadsheet, gsheet: GSheet) -> None:
    last_row = len(gsheet) + 1
    range = f"A2:H{last_row}"

    sorted_rows = sorted([v for v in gsheet.values()], key=lambda v: v.id)

    values = [row.to_gsheet() for row in sorted_rows]

    sh.sheet1.update(range, values)
