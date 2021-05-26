import datetime
from pathlib import Path

import pytest
import pytz

from gpy.config import DEFAULT_TZ
from gpy.types import (
    FileDateReport,
    MediaItem,
    MediaMetadata,
    dates_are_equal,
    structure,
    unstructure,
)


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
    actual_result = dates_are_equal(date_a, date_b)

    assert actual_result == expected_result


def test_structure_report():
    data = {
        "path": "foo/bar.mp4",
        "filename_date": "2019-02-02T18:44:42.000001",
        "metadata_date": "2019-02-02T18:44:43.000001",
        "gps": None,
    }

    report = structure(data, FileDateReport)

    assert report == FileDateReport(
        path=Path("foo/bar.mp4"),
        filename_date=datetime.datetime(2019, 2, 2, 18, 44, 42, 1),
        metadata_date=datetime.datetime(2019, 2, 2, 18, 44, 43, 1),
    )


def test_unstructure_report():
    report = FileDateReport(
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


def test_report_has_google_date():
    report = FileDateReport(
        path=Path("foo/bar.mp4"),
        google_date=datetime.datetime(2019, 2, 2, 18, 44, 42, 1),
    )

    assert report.has_google_date is True


def test_report_has_no_google_date():
    report = FileDateReport(path=Path("foo/bar.mp4"))

    assert report.has_google_date is False


def test_media_metadata_unstrucure():
    media_metadata = MediaMetadata(
        creation_time=datetime.datetime(2004, 4, 29, 13, 25, 43, tzinfo=DEFAULT_TZ),
        width=2048,
        height=1536,
        photo={
            "cameraMake": "BENQ ",
            "cameraModel": "BENQ DC2300",
            "focalLength": 5.6,
            "apertureFNumber": 3.5,
            "isoEquivalent": 100,
            "exposureTime": "0.011111111s",
        },
    )

    data = unstructure(media_metadata)

    assert data == {
        "creationTime": "2004-04-29T13:25:43-00:15",
        "width": 2048,
        "height": 1536,
        "photo": {
            "cameraMake": "BENQ ",
            "cameraModel": "BENQ DC2300",
            "focalLength": 5.6,
            "apertureFNumber": 3.5,
            "isoEquivalent": 100,
            "exposureTime": "0.011111111s",
        },
    }


def test_media_item_unstrucure():
    media_item = MediaItem(
        id="id string",
        product_url="product_url string",
        base_url="base_url string",
        mime_type="image/jpeg",
        media_metadata=MediaMetadata(
            creation_time=datetime.datetime(2004, 4, 29, 13, 25, 43, tzinfo=DEFAULT_TZ),
            width=2048,
            height=1536,
            photo={
                "cameraMake": "BENQ ",
                "cameraModel": "BENQ DC2300",
                "focalLength": 5.6,
                "apertureFNumber": 3.5,
                "isoEquivalent": 100,
                "exposureTime": "0.011111111s",
            },
        ),
        filename="Alex y Bocata.JPG",
        contributor_info=None,
        description=None,
    )

    data = unstructure(media_item)

    assert data == {
        "id": "id string",
        "productUrl": "product_url string",
        "baseUrl": "base_url string",
        "mimeType": "image/jpeg",
        "mediaMetadata": {
            "creationTime": "2004-04-29T13:25:43-00:15",
            "width": 2048,
            "height": 1536,
            "photo": {
                "cameraMake": "BENQ ",
                "cameraModel": "BENQ DC2300",
                "focalLength": 5.6,
                "apertureFNumber": 3.5,
                "isoEquivalent": 100,
                "exposureTime": "0.011111111s",
            },
        },
        "filename": "Alex y Bocata.JPG",
        "contributorInfo": None,
        "description": None,
    }


def test_compare_dates():
    naive_t = datetime.datetime(2012, 1, 1)
    utc_t = datetime.datetime(2012, 1, 1, tzinfo=pytz.utc)
    non_utc_t = datetime.datetime(2012, 1, 1, tzinfo=pytz.timezone("Europe/London"))

    assert dates_are_equal(naive_t, utc_t) is True
    assert dates_are_equal(naive_t, non_utc_t) is False
    assert dates_are_equal(utc_t, non_utc_t) is False
