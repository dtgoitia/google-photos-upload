import datetime

import pytest

from gpy.cli.meta import input_to_datetime


@pytest.mark.parametrize(
    ("input", "expected_result"),
    [
        ("blah", None),
        ("2010-01-01 16:01:01", None),
        ("2010-01-01_16:01:01", datetime.datetime(2010, 1, 1, 16, 1, 1)),
        ("2010-01-01_16:01:01.02", datetime.datetime(2010, 1, 1, 16, 1, 1, 20000)),
    ],
)
def test_input_to_datetime(input, expected_result):
    actual_result = input_to_datetime(input)

    assert actual_result == expected_result
