import datetime

import pytest

from gpy.parsers.filenames import get_datetime_from_filename


@pytest.mark.parametrize(
    ("file_name", "expected_result"),
    [
        ("IMG_20190101_085024_211.jpg", datetime.datetime(2019, 1, 1, 8, 50, 24)),
        ("VID_20190101_085024_211.mp4", datetime.datetime(2019, 1, 1, 8, 50, 24)),
        ("IMG-20190101-WA0001.jpeg", datetime.datetime(2019, 1, 1)),
        ("VID-20190101-WA0001.mp4", datetime.datetime(2019, 1, 1)),
        ("blah", None),
    ],
)
def test_get_datetime_from_filename(file_name, expected_result):
    actual_result = get_datetime_from_filename(file_name)

    assert actual_result == expected_result
