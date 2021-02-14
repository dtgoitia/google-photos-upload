import datetime
from pathlib import Path

import pytest

from gpy.types import Report, _compare_dates, structure, unstructure


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


def test_structure_report():
    data = {
        "path": "foo/bar.mp4",
        "filename_date": "2019-02-02T18:44:42.000001",
        "metadata_date": "2019-02-02T18:44:43.000001",
        "gps": None,
    }

    report = structure(data, Report)

    assert report == Report(
        path=Path("foo/bar.mp4"),
        filename_date=datetime.datetime(2019, 2, 2, 18, 44, 42, 1),
        metadata_date=datetime.datetime(2019, 2, 2, 18, 44, 43, 1),
    )


def test_unstructure_report():
    report = Report(
        path=Path("foo/bar.mp4"),
        filename_date=datetime.datetime(2019, 2, 2, 18, 44, 42, 1),
        metadata_date=datetime.datetime(2019, 2, 2, 18, 44, 43, 1),
    )

    data = unstructure(report)

    assert data == {
        "path": "foo/bar.mp4",
        "filename_date": "2019-02-02T18:44:42.000001",
        "metadata_date": "2019-02-02T18:44:43.000001",
        "google_date": None,
        "gps": None,
    }


def test_structure_datetime():
    data = "2000-01-01T13:45:02.000001"

    d = structure(data, datetime.datetime)

    assert d == datetime.datetime(2000, 1, 1, 13, 45, 2, 1)


def test_unstructure_datetime():
    d = datetime.datetime(2000, 1, 1, 13, 45, 2, 1)

    data = unstructure(d)

    assert data == "2000-01-01T13:45:02.000001"
