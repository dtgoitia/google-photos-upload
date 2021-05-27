import datetime

import pytest
import pytz

from gpy.config import SPAIN, SPAIN_TZ_NAME
from gpy.filenames import build_file_id, parse_datetime


@pytest.mark.parametrize(
    ("file_name", "expected_result"),
    [
        pytest.param(
            "IMG_20190101_085024_211.jpg",
            datetime.datetime(2019, 1, 1, 8, 50, 24),
            id="IMG_YYYYMMDD_hhmmss_XXX.jpg",
        ),
        pytest.param(
            "VID_20190101_085024_211.mp4",
            datetime.datetime(2019, 1, 1, 8, 50, 24),
            id="VID_YYYYMMDD_hhmmss_XXX.mp4",
        ),
        pytest.param(
            "IMG-20190101-WA0001.jpeg",
            datetime.datetime(2019, 1, 1),
            id="IMG-YYYYMMDD-WAXXXX.jpeg",
        ),
        pytest.param(
            "VID-20190101-WA0001.mp4",
            datetime.datetime(2019, 1, 1),
            id="VID-YYYYMMDD-WAXXXX.mp4",
        ),
        pytest.param("blah", None, id="invalid_filename"),
    ],
)
def test_parse_datetime(file_name, expected_result):
    actual_result = parse_datetime(file_name)

    assert actual_result == expected_result


def test_build_file_id_without_timezone():
    ts_no_tz = datetime.datetime(2000, 1, 1)
    ts_utc = ts_no_tz.astimezone(pytz.utc)
    ts_other_tz = ts_utc.astimezone(pytz.timezone(SPAIN_TZ_NAME))

    file_id = build_file_id(file_name="foo", timestamp=ts_no_tz)
    assert file_id == "foo__2000-01-01T00:00:00"


def test_build_file_id_with_timezone():
    ts_no_tz = datetime.datetime(2000, 1, 1)
    ts_utc = ts_no_tz.astimezone(pytz.utc)
    ts_other_tz = ts_utc.astimezone(pytz.timezone(SPAIN_TZ_NAME))

    file_id = build_file_id(file_name="foo", timestamp=ts_utc)
    assert file_id == "foo__2000-01-01T00:00:00"

    file_id = build_file_id(file_name="foo", timestamp=ts_other_tz)
    assert file_id == "foo__2000-01-01T00:00:00"
