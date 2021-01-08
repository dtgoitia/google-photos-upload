import datetime

import pytest

from gpy.cli.meta import input_to_datetime


@pytest.mark.parametrize(
    ("input"),
    [
        pytest.param("blah", id="invalid"),
        pytest.param("2010-01-01 16:01:01", id="wrong formatted date"),
    ],
)
def test_input_to_datetime_with_invalid_datetime(input):
    with pytest.raises(Exception) as e:
        input_to_datetime(input)

    exc = e.value

    assert exc.args == (
        "ERROR: provided input doesn't have the required format "
        "(YYYY-MM-DD_hh:mm:ss.ms)",
    )


@pytest.mark.parametrize(
    ("input", "expected_result"),
    [
        pytest.param(
            "2010-01-01_16:01:01",
            datetime.datetime(2010, 1, 1, 16, 1, 1),
            id="OK",
        ),
        pytest.param(
            "2010-01-01_16:01:01.02",
            datetime.datetime(2010, 1, 1, 16, 1, 1, 20000),
            id="OK with milliseconds",
        ),
    ],
)
def test_input_to_datetime_with_valid_datetime(input, expected_result):
    actual_result = input_to_datetime(input)

    assert actual_result == expected_result
