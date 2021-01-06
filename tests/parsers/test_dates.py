from datetime import datetime

import pytest

from gpy.parsers.dates import try_to_parse_date


@pytest.mark.parametrize(
    ("text", "expected_result"),
    [
        (None, None),
        ("blah", None),
        ("2010-01-01 16:01:01", datetime(2010, 1, 1, 16, 1, 1)),
        ("2010-01-01 16:01:01.00+00.00", datetime(2010, 1, 1, 16, 1, 1)),
    ],
)
def test_try_to_parse_date(text, expected_result):
    actual_result = try_to_parse_date(text)

    assert actual_result == expected_result
