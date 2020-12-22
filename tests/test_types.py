import datetime

import pytest

from gpy.types import _compare_dates


@pytest.mark.parametrize(
    ("date_a", "date_b", "expected_result"),
    [
        pytest.param(
            datetime.datetime(2018, 12, 12, 1, 1, 1, 1),
            datetime.datetime(2018, 12, 12, 1, 1, 1, 2),
            False,
            id="different_dates",
        ),
        pytest.param(
            datetime.datetime(2018, 12, 12, 1, 1, 1, 1),
            datetime.datetime(2018, 12, 12, 1, 1, 1, 1),
            True,
            id="same_dates",
        ),
        pytest.param(
            None,
            datetime.datetime(2018, 12, 12, 1, 1, 1, 1),
            False,
            id="one_date_is_missing",
        ),
        pytest.param(
            None,
            None,
            False,
            id="both_dates_are_missing",
        ),
    ],
)
def test_compare_dates(date_a, date_b, expected_result):
    actual_result = _compare_dates(date_a, date_b)

    assert actual_result == expected_result
