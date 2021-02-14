from unittest.mock import create_autospec

from gspread.models import Spreadsheet, Worksheet

from gpy.google_sheet import GSheetRow, fetch_worksheet


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
