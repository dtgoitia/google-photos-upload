import datetime
from pathlib import Path

import pytest

from gpy.types import Report, _compare_dates, unstructure


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


def test_unstructure_report():
    report = Report(
        path=Path("foo/bar.mp4"),
        filename_date=datetime.datetime(2019, 2, 2, 18, 44, 42),
        metadata_date=datetime.datetime(2019, 2, 2, 18, 44, 43),
    )

    data = unstructure(report)

    assert data == {
        "path": "foo/bar.mp4",
        "filename_date": "2019-02-02 18:44:42.000",
        "metadata_date": "2019-02-02 18:44:43.000",
        "google_date": None,
        "gps": None,
    }
