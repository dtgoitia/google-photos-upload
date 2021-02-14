from typing import Dict, Optional

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
