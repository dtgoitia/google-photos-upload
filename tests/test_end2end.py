"""End to end tests.

These tests simulate the behaviour of a user actually using `gpy` to manipulate
real files (as opposed to mocked ones). All the manipulated files will be
a copy of one or more files in test/statics/. Each test will be provided with
the path of a new temporary directory which will contain the copies of the
mentioned files.

Requirements:
  - `exiftools` installed and available in the PATH
"""

import os
import subprocess
from pathlib import Path
from typing import Set

from click.testing import CliRunner

from gpy.cli.cli import gpy_cli


def test_exiftool_is_installed():
    process = subprocess.run("exiftool -ver", capture_output=True, shell=True)

    assert process.returncode == 0, "exiftool is not installed"

    version = process.stdout.decode().strip()
    assert version == "12.15", "exiftool version is not the expected one"


def test_gpy_scan_date_single(tmp_real_img):
    """Scan date and time for a single file."""
    path = os.path.dirname(tmp_real_img)

    result = CliRunner().invoke(gpy_cli, ["scan", "date", path])

    assert result.output == (
        f"scanning {tmp_real_img}\n"
        "    metadata date and file timestamp don't match\n"
    )
    assert result.exit_code == 0


def test_gpy_scan_date_multiple(tmp_real_files):
    """Scan date and time for multiple files."""
    any_file = tmp_real_files[0]
    dir_path = Path(any_file).parent
    files = [f for f in sorted(tmp_real_files)]

    runner = CliRunner()
    result = runner.invoke(gpy_cli, ["scan", "date", str(dir_path)])
    assert result.output == "\n".join(
        (
            f"scanning {files[0]}",
            "    metadata date and file timestamp don't match",
            f"scanning {files[1]}",
            "    metadata date and file timestamp don't match",
            f"scanning {files[2]}",
            "    metadata date and file timestamp don't match",
            f"scanning {files[3]}",
            f"scanning {files[4]}",
            "",
        )
    )
    assert result.exit_code == 0


def test_gpy_meta_date_fromfile_single_image(tmp_real_img):
    """Set metadata date and time from filename for a single file."""
    path = os.path.dirname(tmp_real_img)
    expected_output1 = (
        f"scanning {tmp_real_img}\n"
        "    metadata date and file timestamp don't match\n"
    )
    expected_output2 = (
        f"writing date 2019-02-02 18:44:42.000 as metadata to {tmp_real_img}\n"
    )
    expected_output3 = f"scanning {tmp_real_img}\n"
    runner = CliRunner()

    result1 = runner.invoke(gpy_cli, ["scan", "date", tmp_real_img])
    result2 = runner.invoke(gpy_cli, ["meta", "date", "--from-filename", path])
    result3 = runner.invoke(gpy_cli, ["scan", "date", tmp_real_img])

    assert result1.output == expected_output1
    assert result1.exception is None
    assert result1.exit_code == 0
    assert result2.output == expected_output2
    assert result2.exception is None
    assert result2.exit_code == 0
    assert result3.output == expected_output3
    assert result3.exception is None
    assert result3.exit_code == 0


def test_gpy_meta_date_fromfile_single_video(tmp_real_vid):
    """Set metadata date and time from filename for a single file."""
    path = os.path.dirname(tmp_real_vid)
    expected_output1 = f"""scanning {tmp_real_vid}\n"""
    expected_output2 = (
        f"writing date 2019-02-02 18:45:13.000 as metadata to {tmp_real_vid}\n"
    )
    expected_output3 = f"scanning {tmp_real_vid}\n"
    runner = CliRunner()

    result1 = runner.invoke(gpy_cli, ["scan", "date", tmp_real_vid])
    result2 = runner.invoke(gpy_cli, ["meta", "date", "--from-filename", path])
    result3 = runner.invoke(gpy_cli, ["scan", "date", tmp_real_vid])

    assert result1.output == expected_output1
    assert result1.exception is None
    assert result1.exit_code == 0
    assert result2.output == expected_output2
    assert result2.exception is None
    assert result2.exit_code == 0
    assert result3.output == expected_output3
    assert result2.exception is None
    assert result3.exit_code == 0


def test_gpy_meta_date_fromfile_multiple(tmp_real_files):
    """Set metadata date and time from filename for multiple files."""
    cmd_path = os.path.dirname(tmp_real_files[0])
    file_paths = [x for x in sorted(tmp_real_files)]
    expected_output3 = ""
    for file in tmp_real_files:
        expected_output3 += f"scanning {file}\n"

    runner = CliRunner()

    result1 = runner.invoke(gpy_cli, ["scan", "date", cmd_path])
    assert result1.exit_code == 0
    assert result1.exception is None
    assert result1.output == (
        f"scanning {file_paths[0]}\n"
        "    metadata date and file timestamp don't match\n"
        f"scanning {file_paths[1]}\n"
        "    metadata date and file timestamp don't match\n"
        f"scanning {file_paths[2]}\n"
        "    metadata date and file timestamp don't match\n"
        f"scanning {file_paths[3]}\n"
        f"scanning {file_paths[4]}\n"
    )

    result2 = runner.invoke(gpy_cli, ["meta", "date", "--from-filename", cmd_path])
    assert result2.output == (
        f"writing date 2019-02-02 18:44:42.000 as metadata to {file_paths[0]}\n"
        f"writing date 2019-02-02 18:44:49.000 as metadata to {file_paths[1]}\n"
        f"writing date 2019-02-02 18:45:20.000 as metadata to {file_paths[2]}\n"
        f"writing date 2019-02-02 18:44:25.000 as metadata to {file_paths[3]}\n"
        f"writing date 2019-02-02 18:45:13.000 as metadata to {file_paths[4]}\n"
    )
    assert result2.exception is None
    assert result2.exit_code == 0

    result3 = runner.invoke(gpy_cli, ["scan", "date", cmd_path])
    assert result3.output == expected_output3
    assert result3.exception is None
    assert result3.exit_code == 0


def test_gpy_meta_date_input_single(tmp_real_img):
    """Set metadata date and time from user input for a single file."""
    runner = CliRunner()

    timestamp = "2010-01-01_00:00:00.01"  # Notice only 2 decimals in millisecs
    result = runner.invoke(
        gpy_cli,
        ["meta", "date", f"--input={timestamp}", tmp_real_img],
    )

    parsed_timestamp = "2010-01-01 00:00:00.010"  # Notice 3 decimals in millisecs
    assert result.output == (
        f"writing date {parsed_timestamp} as metadata to {tmp_real_img}\n"
    )
    assert result.exception is None
    assert result.exit_code == 0


def get_files_in_dir(path: Path) -> Set[Path]:
    return {path for path in path.rglob("*") if path.is_file()}


def test_gpy_meta_date_nobackup_single(tmp_real_img):
    dir_path = Path(tmp_real_img).parent
    files_before = get_files_in_dir(dir_path)
    runner = CliRunner()

    result = runner.invoke(
        gpy_cli,
        ["meta", "date", "--input=2010-01-01_00:00:00", tmp_real_img],
    )

    files_after = get_files_in_dir(dir_path)
    assert files_before == files_after
    assert result.exception is None
    assert result.exit_code == 0


def test_gpy_meta_date_backup_single(tmp_real_img):
    dir_path = Path(tmp_real_img).parent
    files_before = get_files_in_dir(dir_path)
    runner = CliRunner()

    result = runner.invoke(
        gpy_cli,
        ["meta", "date", "--backup", "--input=2010-01-01_00:00:00", tmp_real_img],
    )

    files_after = get_files_in_dir(dir_path)
    assert len(files_before) == 1
    assert len(files_after) == 2
    assert result.exception is None
    assert result.exit_code == 0
