import datetime
from pathlib import Path, PosixPath

import pytest
from py._path.local import LocalPath

from gpy.cli import (
    compare_dates,
    input_to_datetime,
    scan_date,
    scan_gps,
    try_to_parse_date,
)
from gpy.filesystem import get_paths_recursive, is_supported

# -----------------------------------------------------------------------------
# Fixtures


def mkdir(path: Path, dir_name: str) -> Path:
    dir = path / dir_name
    dir.mkdir()
    return dir


@pytest.fixture
def mock_dir(tmp_path: PosixPath, tmpdir: LocalPath) -> Path:
    test_dir = Path(tmp_path)
    (test_dir / "file_1.jpg").write_text("file content 1\n")
    (test_dir / "file_2.png").write_text("file content 2\n")
    (test_dir / "file_3.3gp").write_text("file content 3\n")
    (test_dir / "file_4.mp3").write_text("file content 4\n")
    subdir = mkdir(test_dir, "directory_1")
    (subdir / "file_5.wav").write_text("file content 5\n")
    (subdir / "file_6.mp4").write_text("file content 6\n")

    return test_dir


@pytest.fixture
def parse_mocked(mocker):
    return mocker.patch("gpy.cli.parse")


@pytest.fixture
def read_datetime_mocked(mocker):
    return mocker.patch("gpy.cli.exiftool.read_datetime")


@pytest.fixture
def read_gps_mocked(mocker):
    return mocker.patch("gpy.cli.exiftool.read_gps")


# -----------------------------------------------------------------------------
# Unit tests


@pytest.mark.parametrize(
    ("file_path", "output"),
    [
        pytest.param(Path("file/absolute/path.jpg"), True, id="jpg"),
        pytest.param(Path("file/absolute/path.png"), True, id="png"),
        pytest.param(Path("file/absolute/path.mp4"), True, id="mp4"),
        pytest.param(Path("file/absolute/path.3gp"), True, id="3gp"),
        pytest.param(Path("file/absolute/path.gif"), False, id="gif"),
    ],
)
def test_is_supported(file_path, output):
    assert is_supported(file_path) == output


def test_get_paths_recursive_directory(mock_dir):
    paths = {Path(path) for path in get_paths_recursive(root_path=mock_dir)}

    assert paths == {
        mock_dir / "file_3.3gp",
        mock_dir / "file_2.png",
        mock_dir / "file_1.jpg",
        mock_dir / "directory_1" / "file_6.mp4",
    }


def test_get_paths_recursive_file(tmp_path):
    file_path: Path = tmp_path / "file_1.jpg"
    file_path.touch()

    paths = {p for p in get_paths_recursive(root_path=file_path)}

    assert paths == {file_path}


@pytest.mark.parametrize(
    ("path", "read_datetime_return", "parse_return", "expected_result"),
    [
        pytest.param(
            Path("blah/foo.mp4"),
            None,
            None,
            {
                "filename_date": None,
                "match_date": False,
                "metadata_date": None,
                "path": Path("blah/foo.mp4"),
            },
            id="filename_with_no_date_or_no_metadata_or_broken_metadata",
        ),
        pytest.param(
            Path("blah/foo.mp4"),
            "2010-01-01 16:01:01",
            None,
            {
                "filename_date": None,
                "match_date": False,
                "metadata_date": datetime.datetime(2010, 1, 1, 16, 1, 1),
                "path": Path("blah/foo.mp4"),
            },
            id="filename_with_no_date_but_metadata_OK",
        ),
        pytest.param(
            Path("blah/VID_20100101_160101_123.mp4"),
            None,
            datetime.datetime(2010, 1, 1, 16, 1, 1),
            {
                "filename_date": datetime.datetime(2010, 1, 1, 16, 1, 1),
                "match_date": False,
                "metadata_date": None,
                "path": Path("blah/VID_20100101_160101_123.mp4"),
            },
            id="filename_ok_but_no_metadata_or_broken_metadata",
        ),
        pytest.param(
            Path("blah/VID_20100101_160101_123.mp4"),
            "2012-02-02 17:02:02",
            datetime.datetime(2010, 1, 1, 16, 1, 1),
            {
                "filename_date": datetime.datetime(2010, 1, 1, 16, 1, 1),
                "match_date": False,
                "metadata_date": datetime.datetime(2012, 2, 2, 17, 2, 2),
                "path": Path("blah/VID_20100101_160101_123.mp4"),
            },
            id="filename_ok_and_metadata_ok_but_dates_do_not_match",
        ),
        pytest.param(
            Path("blah/VID_20100101_160101_123.mp4"),
            "2010-01-01 16:01:01",
            datetime.datetime(2010, 1, 1, 16, 1, 1),
            {
                "filename_date": datetime.datetime(2010, 1, 1, 16, 1, 1),
                "match_date": True,
                "metadata_date": datetime.datetime(2010, 1, 1, 16, 1, 1),
                "path": Path("blah/VID_20100101_160101_123.mp4"),
            },
            id="filename_ok_and_metadata_ok_and_dates_match",
        ),
        pytest.param(
            Path("blah/VID_20100101_160101_123.mp4"),
            "2010-01-01 16:01:01.00+00.00",
            datetime.datetime(2010, 1, 1, 16, 1, 1),
            {
                "filename_date": datetime.datetime(2010, 1, 1, 16, 1, 1),
                "match_date": True,
                "metadata_date": datetime.datetime(2010, 1, 1, 16, 1, 1),
                "path": Path("blah/VID_20100101_160101_123.mp4"),
            },
            id="filename_ok_and_metadata_ok_with_timezone_+0h_and_dates_match",
        ),
        pytest.param(
            Path("blah/VID_20100101_160101_123.mp4"),
            "2010-01-01 16:01:01.00+05.00",
            datetime.datetime(2010, 1, 1, 16, 1, 1),
            {
                "filename_date": datetime.datetime(2010, 1, 1, 16, 1, 1),
                "match_date": True,
                "metadata_date": datetime.datetime(2010, 1, 1, 16, 1, 1),
                "path": Path("blah/VID_20100101_160101_123.mp4"),
            },
            id="filename_ok_and_metadata_ok_with_timezone_+5h_and_dates_match",
        ),
    ],
)
def test_scan_date(
    read_datetime_mocked,
    parse_mocked,
    path,
    read_datetime_return,
    parse_return,
    expected_result,
):
    read_datetime_mocked.return_value = read_datetime_return
    parse_mocked.return_value = parse_return

    actual_result = scan_date(file_path=path)

    assert actual_result == expected_result


@pytest.mark.parametrize(
    ("text", "expected_result"),
    [
        (None, None),
        ("blah", None),
        ("2010-01-01 16:01:01", datetime.datetime(2010, 1, 1, 16, 1, 1)),
        ("2010-01-01 16:01:01.00+00.00", datetime.datetime(2010, 1, 1, 16, 1, 1)),
    ],
)
def test_try_to_parse_date(text, expected_result):
    actual_result = try_to_parse_date(text)

    assert actual_result == expected_result


@pytest.mark.skip(reason="not implemented")
@pytest.mark.parametrize(
    ("return_value", "expected_result"),
    [
        ("random_coords", {"path": "random_path", "gps": "random_coords"}),
        (None, {"path": "random_path"}),
    ],
)
def test_scan_gps(read_gps_mocked, return_value, expected_result):
    read_gps_mocked.return_value = return_value

    actual_result = scan_gps(file_path=Path("random_path"))

    assert actual_result == expected_result


@pytest.mark.parametrize(
    ("date_a", "date_b", "expected_result"),
    [
        (
            datetime.datetime(2018, 12, 12, 1, 1, 1, 1),
            datetime.datetime(2018, 12, 12, 1, 1, 1, 2),
            False,
        ),
        (
            datetime.datetime(2018, 12, 12, 1, 1, 1, 1),
            datetime.datetime(2018, 12, 12, 1, 1, 1, 1),
            True,
        ),
        (None, datetime.datetime(2018, 12, 12, 1, 1, 1, 1), False),
        (None, None, False),
    ],
)
def test_compare_dates(date_a, date_b, expected_result):
    actual_result = compare_dates(date_a, date_b)

    assert actual_result == expected_result


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
