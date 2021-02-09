"""End to end tests.

These tests simulate the behaviour of a user actually using `gpy` to manipulate
real files (as opposed to mocked ones). All the manipulated files will be
a copy of one or more files in test/statics/. Each test will be provided with
the path of a new temporary directory which will contain the copies of the
mentioned files.

Requirements:
  - `exiftools` installed and available in the PATH
"""

import datetime
import logging
import subprocess
from pathlib import Path
from typing import List, Set

from _pytest.logging import LogCaptureFixture as LogCapture

from gpy.cli.meta import edit_metadata_datetime
from gpy.cli.scan import _scan_date, scan_date
from gpy.exiftool import client as exiftool_client
from gpy.filenames import parse_datetime as datetime_parser
from gpy.types import Report


def test_exiftool_is_installed():
    process = subprocess.run("exiftool -ver", capture_output=True, shell=True)

    assert process.returncode == 0, "exiftool is not installed"

    version = process.stdout.decode().strip()
    mayor, _ = version.split(".")
    assert mayor == "12", "exiftool version is not the expected one"


def test_gpy_scan_date_single(tmp_real_img: Path, caplog: LogCapture) -> None:
    """Scan date and time for a single file."""
    caplog.set_level(logging.INFO)

    report = _scan_date(exiftool_client, datetime_parser, tmp_real_img)

    assert report == Report(
        path=tmp_real_img,
        metadata_date=datetime.datetime(2019, 2, 2, 18, 44, 43),
        filename_date=datetime.datetime(2019, 2, 2, 18, 44, 42),
    )

    printed_output = "\n".join(caplog.messages)
    assert printed_output == (
        f"scanning {tmp_real_img}\n"
        "    metadata date and file timestamp don't match:\n"
        "      > metadata: 2019-02-02 18:44:43.000\n"
        "      > filename: 2019-02-02 18:44:42.000"
    )


def test_gpy_scan_date_multiple(tmp_real_files: List[Path], caplog: LogCapture) -> None:
    """Scan date and time for multiple files."""
    caplog.set_level(logging.INFO)

    dir_path = tmp_real_files[0].parent

    img_1, img_2, img_3, vid_1, vid_2 = [f for f in sorted(tmp_real_files)]

    reports = scan_date(exiftool_client, datetime_parser, dir_path)

    assert reports == [
        Report(
            path=img_1,
            metadata_date=datetime.datetime(2019, 2, 2, 18, 44, 43),
            filename_date=datetime.datetime(2019, 2, 2, 18, 44, 42),
        ),
        Report(
            path=img_2,
            metadata_date=datetime.datetime(2019, 2, 2, 18, 44, 58),
            filename_date=datetime.datetime(2019, 2, 2, 18, 44, 49),
        ),
        Report(
            path=img_3,
            metadata_date=datetime.datetime(2019, 2, 2, 18, 45, 21),
            filename_date=datetime.datetime(2019, 2, 2, 18, 45, 20),
        ),
        Report(
            path=vid_1,
            metadata_date=datetime.datetime(2019, 2, 2, 18, 44, 25),
            filename_date=datetime.datetime(2019, 2, 2, 18, 44, 25),
        ),
        Report(
            path=vid_2,
            metadata_date=datetime.datetime(2019, 2, 2, 18, 45, 13),
            filename_date=datetime.datetime(2019, 2, 2, 18, 45, 13),
        ),
    ]

    printed_output = "\n".join(caplog.messages)
    assert printed_output == (
        f"scanning {img_1}\n"
        "    metadata date and file timestamp don't match:\n"
        "      > metadata: 2019-02-02 18:44:43.000\n"
        "      > filename: 2019-02-02 18:44:42.000\n"
        f"scanning {img_2}\n"
        "    metadata date and file timestamp don't match:\n"
        "      > metadata: 2019-02-02 18:44:58.000\n"
        "      > filename: 2019-02-02 18:44:49.000\n"
        f"scanning {img_3}\n"
        "    metadata date and file timestamp don't match:\n"
        "      > metadata: 2019-02-02 18:45:21.000\n"
        "      > filename: 2019-02-02 18:45:20.000\n"
        f"scanning {vid_1}\n"
        f"scanning {vid_2}"
    )


def test_gpy_meta_date_fromfile_single_image(
    tmp_real_img: Path, caplog: LogCapture
) -> None:
    """Set metadata date and time from filename for a single file."""
    caplog.set_level(logging.INFO)

    # Scan file dates
    reports_1 = scan_date(exiftool_client, datetime_parser, tmp_real_img)
    assert reports_1 == [
        Report(
            path=tmp_real_img,
            metadata_date=datetime.datetime(2019, 2, 2, 18, 44, 43),
            filename_date=datetime.datetime(2019, 2, 2, 18, 44, 42),
        ),
    ]

    # Update metadata date to match filename date
    reports_2 = edit_metadata_datetime(
        path=tmp_real_img,
        read_datetime_from_filename=True,
        input=None,
        backup=False,
    )  # type: ignore
    assert reports_2 is None  # TODO: it should be a report, not None

    # Scan file dates
    reports_3 = scan_date(exiftool_client, datetime_parser, tmp_real_img)
    assert reports_3 == [
        Report(
            path=tmp_real_img,
            metadata_date=datetime.datetime(2019, 2, 2, 18, 44, 42),
            filename_date=datetime.datetime(2019, 2, 2, 18, 44, 42),
        ),
    ]

    printed_output = "\n".join(caplog.messages)
    assert printed_output == (
        f"scanning {tmp_real_img}\n"
        "    metadata date and file timestamp don't match:\n"
        "      > metadata: 2019-02-02 18:44:43.000\n"
        "      > filename: 2019-02-02 18:44:42.000\n"
        f"writing date 2019-02-02 18:44:42.000 as metadata to {tmp_real_img}\n"
        f"scanning {tmp_real_img}"
    )


def test_gpy_meta_date_fromfile_multiple(
    tmp_real_files: List[Path], caplog: LogCapture
) -> None:
    """Set metadata datetime from filename for multiple files."""
    caplog.set_level(logging.INFO)

    # TODO: remove once `tmp_real_files` is a Path, instead of str
    dir_path = tmp_real_files[0].parent

    img_1, img_2, img_3, vid_1, vid_2 = [f for f in sorted(tmp_real_files)]

    scan_date(exiftool_client, datetime_parser, dir_path)
    edit_metadata_datetime(
        path=dir_path,
        read_datetime_from_filename=True,
        input=None,
        backup=False,
    )
    scan_date(exiftool_client, datetime_parser, dir_path)

    printed_output = "\n".join(caplog.messages)
    assert printed_output == (
        f"scanning {img_1}\n"
        "    metadata date and file timestamp don't match:\n"
        "      > metadata: 2019-02-02 18:44:43.000\n"
        "      > filename: 2019-02-02 18:44:42.000\n"
        f"scanning {img_2}\n"
        "    metadata date and file timestamp don't match:\n"
        "      > metadata: 2019-02-02 18:44:58.000\n"
        "      > filename: 2019-02-02 18:44:49.000\n"
        f"scanning {img_3}\n"
        "    metadata date and file timestamp don't match:\n"
        "      > metadata: 2019-02-02 18:45:21.000\n"
        "      > filename: 2019-02-02 18:45:20.000\n"
        f"scanning {vid_1}\n"
        f"scanning {vid_2}\n"
        f"writing date 2019-02-02 18:44:42.000 as metadata to {img_1}\n"
        f"writing date 2019-02-02 18:44:49.000 as metadata to {img_2}\n"
        f"writing date 2019-02-02 18:45:20.000 as metadata to {img_3}\n"
        f"writing date 2019-02-02 18:44:25.000 as metadata to {vid_1}\n"
        f"writing date 2019-02-02 18:45:13.000 as metadata to {vid_2}\n"
        f"scanning {img_1}\n"
        f"scanning {img_2}\n"
        f"scanning {img_3}\n"
        f"scanning {vid_1}\n"
        f"scanning {vid_2}"
    )


def test_gpy_meta_date_input_single(tmp_real_img: Path, caplog: LogCapture) -> None:
    """Set metadata datetime from user input for a single file."""
    caplog.set_level(logging.INFO)

    user_input = "2010-01-01_00:00:00.01"  # Notice only 2 decimals in millisecs
    scan_date(exiftool_client, datetime_parser, tmp_real_img)
    edit_metadata_datetime(
        path=tmp_real_img,
        read_datetime_from_filename=False,
        input=user_input,
        backup=False,
    )
    scan_date(exiftool_client, datetime_parser, tmp_real_img)

    printed_output = "\n".join(caplog.messages)
    assert printed_output == (
        f"scanning {tmp_real_img}\n"
        "    metadata date and file timestamp don't match:\n"
        "      > metadata: 2019-02-02 18:44:43.000\n"
        "      > filename: 2019-02-02 18:44:42.000\n"
        f"writing date 2010-01-01 00:00:00.010 as metadata to {tmp_real_img}\n"
        f"scanning {tmp_real_img}\n"
        "    metadata date and file timestamp don't match:\n"
        "      > metadata: 2010-01-01 00:00:00.000\n"
        "      > filename: 2019-02-02 18:44:42.000"
    )


def get_files_in_dir(path: Path) -> Set[Path]:
    return {path for path in path.rglob("*") if path.is_file()}


def test_gpy_meta_date_nobackup_single(tmp_real_img: Path, caplog: LogCapture) -> None:
    """Set metadata datetime from user input for a single file and don't backup."""
    caplog.set_level(logging.INFO)

    dir_path = tmp_real_img.parent

    files_before = get_files_in_dir(dir_path)

    edit_metadata_datetime(
        path=tmp_real_img,
        read_datetime_from_filename=False,
        input="2010-01-01_00:00:00.01",
        backup=False,
    )

    files_after = get_files_in_dir(dir_path)

    assert files_before == files_after


def test_gpy_meta_date_backup_single(tmp_real_img: Path, caplog: LogCapture) -> None:
    """Set metadata datetime from user input for a single file and keep a backup."""
    caplog.set_level(logging.INFO)

    dir_path = tmp_real_img.parent

    files_before = get_files_in_dir(dir_path)

    edit_metadata_datetime(
        path=tmp_real_img,
        read_datetime_from_filename=False,
        input="2010-01-01_00:00:00.01",
        backup=True,
    )

    files_after = get_files_in_dir(dir_path)

    assert len(files_before) == 1
    assert len(files_after) == 2
