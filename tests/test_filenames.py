import datetime

import pytest

from gpy.filenames import parse


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
def test_main_file_name_parser(file_name, expected_result):
    actual_result = parse(file_name)

    assert actual_result == expected_result
