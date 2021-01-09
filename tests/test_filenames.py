import datetime

import pytest

from gpy.filenames import parse_datetime


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
