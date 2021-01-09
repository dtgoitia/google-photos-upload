import datetime
from pathlib import Path
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

import pytest

from gpy.cli.scan import scan_date, scan_gps
from gpy.types import Report

TZ = ZoneInfo("Europe/Madrid")


@pytest.fixture
def parse_mocked(mocker):
    # TODO: refactor to avoid monkey-patching and use DI instead
    return mocker.patch("gpy.parsers.filenames.parse_datetime")


@pytest.fixture
def read_datetime_mocked(mocker):
    # TODO: refactor to avoid monkey-patching and use DI instead
    return mocker.patch("gpy.exiftool.client.read_datetime")


@pytest.fixture
def read_gps_mocked(mocker):
    # TODO: refactor to avoid monkey-patching and use DI instead
    return mocker.patch("gpy.exiftool.client.read_gps")


@pytest.mark.parametrize(
    ("path", "read_datetime_return", "parse_return", "expected_result"),
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
            datetime.datetime(2010, 1, 1, 16, 1, 1),
            None,
            Report(
                filename_date=None,
                metadata_date=datetime.datetime(2010, 1, 1, 16, 1, 1),
                path=Path("blah/foo.mp4"),
            ),
            id="filename_with_no_date_but_metadata_OK",
        ),
        pytest.param(
            Path("blah/VID_20100101_160101_123.mp4"),
            None,
            datetime.datetime(2010, 1, 1, 16, 1, 1),
            Report(
                filename_date=datetime.datetime(2010, 1, 1, 16, 1, 1),
                metadata_date=None,
                path=Path("blah/VID_20100101_160101_123.mp4"),
            ),
            id="filename_ok_but_no_metadata_or_broken_metadata",
        ),
        pytest.param(
            Path("blah/VID_20100101_160101_123.mp4"),
            datetime.datetime(2012, 2, 2, 17, 2, 2),
            datetime.datetime(2010, 1, 1, 16, 1, 1),
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
            datetime.datetime(2010, 1, 1, 16, 1, 1, tzinfo=TZ),
            datetime.datetime(2010, 1, 1, 16, 1, 1),
            Report(
                filename_date=datetime.datetime(2010, 1, 1, 16, 1, 1),
                metadata_date=datetime.datetime(2010, 1, 1, 16, 1, 1, tzinfo=TZ),
                path=Path("blah/VID_20100101_160101_123.mp4"),
            ),
            id="filename_ok_and_metadata_ok_with_timezone_and_dates_match",
        ),
    ],
)
def test_scan_date(
    parse_mocked,
    path,
    read_datetime_return,
    parse_return,
    expected_result,
):
    parse_mocked.return_value = parse_return

    mocked_client = MagicMock()
    mocked_client.read_datetime.return_value = read_datetime_return

    actual_result = scan_date(exiftool=mocked_client, path=path)

    assert actual_result == expected_result


@pytest.mark.skip(reason="not implemented")
@pytest.mark.parametrize(
    ("return_value", "expected_result"),
    [
        ("random_coords", {"path": "random_path", "gps": "random_coords"}),
        (None, {"path": "random_path"}),
    ],
)
def test_scan_gps(return_value, expected_result):
    mocked_client = MagicMock()
    mocked_client.read_gps.return_value = return_value

    actual_result = scan_gps(mocked_client, file_path=Path("random_path"))

    assert actual_result == expected_result
