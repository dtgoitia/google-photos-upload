"""End to end tests.

These tests simulate the behaviour of a user actually using `gpy` to manipulate
real files (as opposed to mocked ones). All the manipulated files will be
a copy of one or more files in test/statics/. Each test will be provided with
the path of a new temporary directory which will contain the copies of the
mentioned files.

Requirements:
  - `exiftools` installed and available in the PATH
"""

from click.testing import CliRunner
from gpy import cli
import os
import pytest


def test_gpy_scan_date_single(tmp_real_img):
    """Scan date and time for a single file."""
    path = os.path.dirname(tmp_real_img)
    expected_output = f"""scanning {tmp_real_img}
    metadata date and file timestamp don't match\n"""
    runner = CliRunner()

    result = runner.invoke(cli.main, ['scan', 'date', path])

    assert result.exit_code == 0
    assert result.output == expected_output


def test_gpy_scan_date_multiple(tmp_real_files):
    """Scan date and time for multiple files."""
    path = os.path.dirname(tmp_real_files[0])
    files = [x for x in reversed(tmp_real_files)]
    expected_output = f"""scanning {files[0]}
scanning {files[1]}
scanning {files[2]}
    metadata date and file timestamp don't match
scanning {files[3]}
    metadata date and file timestamp don't match
scanning {files[4]}
    metadata date and file timestamp don't match
"""

    runner = CliRunner()
    result = runner.invoke(cli.main, ['scan', 'date', path])
    assert result.exit_code == 0
    assert result.output == expected_output


def test_gpy_meta_date_fromfile_single_image(tmp_real_img):
    """Set metadata date and time from filename for a single file."""
    path = os.path.dirname(tmp_real_img)
    expected_output1 = f"""scanning {tmp_real_img}
    metadata date and file timestamp don't match\n"""
    expected_output2 = f'writing date 2019-02-02 18:44:42 as metadata to {tmp_real_img}\n'
    expected_output3 = f'scanning {tmp_real_img}\n'
    runner = CliRunner()

    result1 = runner.invoke(cli.main, ['scan', 'date', tmp_real_img])
    result2 = runner.invoke(cli.main, ['meta', 'date', '--from-filename', path])
    result3 = runner.invoke(cli.main, ['scan', 'date', tmp_real_img])

    assert result1.exit_code == 0
    assert result2.exit_code == 0
    assert result3.exit_code == 0
    assert result1.output == expected_output1
    assert result2.output == expected_output2
    assert result3.output == expected_output3


def test_gpy_meta_date_fromfile_single_video(tmp_real_vid):
    """Set metadata date and time from filename for a single file."""
    path = os.path.dirname(tmp_real_vid)
    expected_output1 = f"""scanning {tmp_real_vid}\n"""
    expected_output2 = f'writing date 2019-02-02 18:45:13 as metadata to {tmp_real_vid}\n'
    expected_output3 = f'scanning {tmp_real_vid}\n'
    runner = CliRunner()

    result1 = runner.invoke(cli.main, ['scan', 'date', tmp_real_vid])
    result2 = runner.invoke(cli.main, ['meta', 'date', '--from-filename', path])
    result3 = runner.invoke(cli.main, ['scan', 'date', tmp_real_vid])

    assert result1.exit_code == 0
    assert result2.exit_code == 0
    assert result3.exit_code == 0
    assert result1.output == expected_output1
    assert result2.output == expected_output2
    assert result3.output == expected_output3


def test_gpy_meta_date_fromfile_multiple(tmp_real_files):
    """Set metadata date and time from filename for multiple files."""
    path = os.path.dirname(tmp_real_files[0])
    files = [x for x in reversed(tmp_real_files)]
    expected_output1 = f"""scanning {files[0]}
scanning {files[1]}
scanning {files[2]}
    metadata date and file timestamp don't match
scanning {files[3]}
    metadata date and file timestamp don't match
scanning {files[4]}
    metadata date and file timestamp don't match
"""
    expected_output2 = f"""writing date 2019-02-02 18:45:13 as metadata to {files[0]}
writing date 2019-02-02 18:44:25 as metadata to {files[1]}
writing date 2019-02-02 18:45:20 as metadata to {files[2]}
writing date 2019-02-02 18:44:49 as metadata to {files[3]}
writing date 2019-02-02 18:44:42 as metadata to {files[4]}
"""
    expected_output3 = ''
    for file in tmp_real_files:
        expected_output3 += f'scanning {file}\n'
    runner = CliRunner()

    result1 = runner.invoke(cli.main, ['scan', 'date', path])
    result2 = runner.invoke(cli.main, ['meta', 'date', '--from-filename', path])
    result3 = runner.invoke(cli.main, ['scan', 'date', path])

    assert result1.exit_code == 0
    assert result2.exit_code == 0
    assert result3.exit_code == 0
    assert result1.output == expected_output1
    assert result2.output == expected_output2
    assert result3.output == expected_output3


def test_gpy_meta_date_input_single(tmp_real_img):
    """Set metadata date and time from user input for a single file."""
    runner = CliRunner()

    result = runner.invoke(cli.main, ['meta', 'date', '--input=2010-01-01_00:00:00', tmp_real_img])

    assert result.exit_code == 0
    assert result.output == f'writing date 2010-01-01 00:00:00 as metadata to {tmp_real_img}\n'


def test_gpy_meta_date_nobackup_single(tmp_real_img):
    path = os.path.dirname(tmp_real_img)
    files_before = [x[2] for x in os.walk(path)][0]
    runner = CliRunner()

    result = runner.invoke(cli.main, ['meta', 'date', '--no-backup', '--input=2010-01-01_00:00:00', tmp_real_img])

    assert result.exit_code == 0
    files_after = [x[2] for x in os.walk(path)][0]
    assert len(files_before) == 1
    assert len(files_after) == 1


def test_gpy_meta_date_backup_single(tmp_real_img):
    path = os.path.dirname(tmp_real_img)
    files_before = [x[2] for x in os.walk(path)][0]
    runner = CliRunner()

    result = runner.invoke(cli.main, ['meta', 'date', '--input=2010-01-01_00:00:00', tmp_real_img])

    assert result.exit_code == 0
    files_after = [x[2] for x in os.walk(path)][0]
    assert len(files_before) == 1
    assert len(files_after) == 2
