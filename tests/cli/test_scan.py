import datetime
from pathlib import Path
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

import pytest

from gpy.cli.scan import _scan_date, scan_gps
from gpy.types import Report

TZ = ZoneInfo("Europe/Madrid")


@pytest.mark.parametrize(
    ("path", "filename_datetime", "metadata_datetime", "expected_result"),
    [
        pytest.param(
            Path("blah/foo.mp4"),
            None,
            None,
            Report(
                filename_date=None,
                metadata_date=None,
                path=Path("blah/foo.mp4"),
            ),
            id="filename_with_no_date_or_no_metadata_or_broken_metadata",
        ),
        pytest.param(
            Path("blah/foo.mp4"),
            None,
            datetime.datetime(2010, 1, 1, 16, 1, 1),
            Report(
                filename_date=None,
                metadata_date=datetime.datetime(2010, 1, 1, 16, 1, 1),
                path=Path("blah/foo.mp4"),
            ),
            id="filename_with_no_date_but_metadata_OK",
        ),
        pytest.param(
            Path("blah/VID_20100101_160101_123.mp4"),
            datetime.datetime(2010, 1, 1, 16, 1, 1),
            None,
            Report(
                filename_date=datetime.datetime(2010, 1, 1, 16, 1, 1),
                metadata_date=None,
                path=Path("blah/VID_20100101_160101_123.mp4"),
            ),
            id="filename_ok_but_no_metadata_or_broken_metadata",
        ),
        pytest.param(
            Path("blah/VID_20100101_160101_123.mp4"),
            datetime.datetime(2010, 1, 1, 16, 1, 1),
            datetime.datetime(2012, 2, 2, 17, 2, 2),
            Report(
                filename_date=datetime.datetime(2010, 1, 1, 16, 1, 1),
                metadata_date=datetime.datetime(2012, 2, 2, 17, 2, 2),
                path=Path("blah/VID_20100101_160101_123.mp4"),
            ),
            id="filename_ok_and_metadata_ok_but_dates_do_not_match",
        ),
        pytest.param(
            Path("blah/VID_20100101_160101_123.mp4"),
            datetime.datetime(2010, 1, 1, 16, 1, 1),
            datetime.datetime(2010, 1, 1, 16, 1, 1),
            Report(
                filename_date=datetime.datetime(2010, 1, 1, 16, 1, 1),
                metadata_date=datetime.datetime(2010, 1, 1, 16, 1, 1),
                path=Path("blah/VID_20100101_160101_123.mp4"),
            ),
            id="filename_ok_and_metadata_ok_and_dates_match",
        ),
        pytest.param(
            Path("blah/VID_20100101_160101_123.mp4"),
            datetime.datetime(2010, 1, 1, 16, 1, 1),
            datetime.datetime(2010, 1, 1, 16, 1, 1, tzinfo=TZ),
            Report(
                filename_date=datetime.datetime(2010, 1, 1, 16, 1, 1),
                metadata_date=datetime.datetime(2010, 1, 1, 16, 1, 1, tzinfo=TZ),
                path=Path("blah/VID_20100101_160101_123.mp4"),
            ),
            id="filename_ok_and_metadata_ok_with_timezone_and_dates_match",
        ),
    ],
)
def test_scan_single_file_date(
    path: Path,
    filename_datetime: datetime.datetime,
    metadata_datetime: datetime.datetime,
    expected_result: Report,
) -> None:
    parser_mock = MagicMock()
    parser_mock.return_value = filename_datetime

    exiftool_client_mock = MagicMock()
    exiftool_client_mock.read_datetime.return_value = metadata_datetime
    exiftool_client_mock.read_google_timestamp.return_value = None

    actual_result = _scan_date(
        exiftool=exiftool_client_mock,
        parse_datetime=parser_mock,
        path=path,
    )

    assert actual_result == expected_result


@pytest.mark.skip(reason="not implemented")
@pytest.mark.parametrize(
    ("metadata_gps", "expected_result"),
    [
        ("random_coords", {"path": "random_path", "gps": "random_coords"}),
        (None, {"path": "random_path"}),
    ],
)
def test_scan_gps(metadata_gps, expected_result):
    mocked_client = MagicMock()
    mocked_client.read_gps.return_value = metadata_gps

    actual_result = scan_gps(mocked_client, file_path=Path("random_path"))

    assert actual_result == expected_result
