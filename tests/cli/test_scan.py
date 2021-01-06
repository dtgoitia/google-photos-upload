import datetime
from pathlib import Path

import pytest

from gpy.cli.scan import scan_date, scan_gps
from gpy.types import Report


@pytest.fixture
def parse_mocked(mocker):
    # TODO: refactor to avoid monkey-patching and use DI instead
    return mocker.patch("gpy.parsers.filenames.get_datetime_from_filename")


@pytest.fixture
def read_datetime_mocked(mocker):
    # TODO: refactor to avoid monkey-patching and use DI instead
    return mocker.patch("gpy.exiftool.read_datetime")


@pytest.fixture
def read_gps_mocked(mocker):
    # TODO: refactor to avoid monkey-patching and use DI instead
    return mocker.patch("gpy.exiftool.read_gps")


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
            "2010-01-01 16:01:01",
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
            "2012-02-02 17:02:02",
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
            "2010-01-01 16:01:01",
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
            "2010-01-01 16:01:01.00+00.00",
            datetime.datetime(2010, 1, 1, 16, 1, 1),
            Report(
                filename_date=datetime.datetime(2010, 1, 1, 16, 1, 1),
                metadata_date=datetime.datetime(2010, 1, 1, 16, 1, 1),
                path=Path("blah/VID_20100101_160101_123.mp4"),
            ),
            id="filename_ok_and_metadata_ok_with_timezone_+0h_and_dates_match",
        ),
        pytest.param(
            Path("blah/VID_20100101_160101_123.mp4"),
            "2010-01-01 16:01:01.00+05.00",
            datetime.datetime(2010, 1, 1, 16, 1, 1),
            Report(
                filename_date=datetime.datetime(2010, 1, 1, 16, 1, 1),
                metadata_date=datetime.datetime(2010, 1, 1, 16, 1, 1),
                path=Path("blah/VID_20100101_160101_123.mp4"),
            ),
            id="filename_ok_and_metadata_ok_with_timezone_+5h_and_dates_match",
        ),
    ],
)
def test_scan_date(
    read_datetime_mocked,
    parse_mocked,
    path,
    read_datetime_return,
    parse_return,
    expected_result,
):
    read_datetime_mocked.return_value = read_datetime_return
    parse_mocked.return_value = parse_return

    actual_result = scan_date(file_path=path)

    assert actual_result == expected_result


@pytest.mark.skip(reason="not implemented")
@pytest.mark.parametrize(
    ("return_value", "expected_result"),
    [
        ("random_coords", {"path": "random_path", "gps": "random_coords"}),
        (None, {"path": "random_path"}),
    ],
)
def test_scan_gps(read_gps_mocked, return_value, expected_result):
    read_gps_mocked.return_value = return_value

    actual_result = scan_gps(file_path=Path("random_path"))

    assert actual_result == expected_result
