from pathlib import Path
from unittest.mock import create_autospec

from gspread.models import Spreadsheet, Worksheet

from gpy.google_sheet import FileReport, GSheetRow, fetch_worksheet


def test_gsheetrow_to_gsheet():
    gsheet_row = GSheetRow(
        id="foo/bar/baz.png",
        last_filename="baz.png",
        last_dir="foo/bar",
        dates_match=True,
        has_ghotos_timestamp=False,
        uploaded=False,
        album=None,
    )

    assert gsheet_row.to_gsheet() == [
        "foo/bar/baz.png",
        "baz.png",
        "foo/bar",
        True,
        False,
        False,
        "",
        "",
    ]


def test_filereport_to_gsheetrow():
    file_report = FileReport(
        path=Path("foo/bar/baz.png"),
        dates_match=True,
        has_ghotos_timestamp=False,
        uploaded=False,
    )

    assert file_report.to_gsheet_row() == GSheetRow(
        id="foo/bar/baz.png",
        last_filename="baz.png",
        last_dir="foo/bar",
        dates_match=True,
        has_ghotos_timestamp=False,
        uploaded=False,
        album=None,
    )


def test_fetch_worksheet():
    records = (
        {
            "ID": "id1",
            "Last filename": "nam1",
            "Last dir": "dir1",
            "Filename and metadata dates do match": "FALSE",
            "has GPhotos timestamp": "TRUE",
            "uploaded": "FALSE",
            "albumId": "",
            "albumName": "",
        },
    )
    mock_worksheet = create_autospec(Worksheet)
    mock_worksheet.get_all_records.return_value = (r for r in records)
    mock_spreadsheet = create_autospec(Spreadsheet)
    mock_spreadsheet.sheet1 = mock_worksheet

    gsheet = fetch_worksheet(mock_spreadsheet)

    assert gsheet == {
        "id1": GSheetRow(
            id="id1",
            last_filename="nam1",
            last_dir="dir1",
            dates_match=False,
            has_ghotos_timestamp=True,
            uploaded=False,
            album=None,
        )
    }
