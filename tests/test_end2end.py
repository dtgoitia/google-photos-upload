"""End to end tests.

These tests simulate the behaviour of a user actually using `gpy` to manipulate
real files (as opposed to mocked ones). All the manipulated files will be
a copy of one or more files in test/statics/. Each test will be provided with
the path of a new temporary directory which will contain the copies of the
mentioned files.

Requirements:
  - `exiftools` installed and available in the PATH
"""

from gpy import cli
import os
from click.testing import CliRunner


def test_scan_single_file(tmp_real_img):
    path = os.path.dirname(tmp_real_img)
    expected_output = f"""scanning {tmp_real_img}
    metadata date and file timestamp don't match\n"""

    runner = CliRunner()
    result = runner.invoke(cli.main, ['scan', 'date', path])
    assert result.exit_code == 0
    assert result.output == expected_output


def test_scan_multiple_files(tmp_real_files):
    path = os.path.dirname(tmp_real_files[0])
    expected_output = ""
    for file in reversed(tmp_real_files):
        expected_output += f"""scanning {file}
    metadata date and file timestamp don't match\n"""

    runner = CliRunner()
    result = runner.invoke(cli.main, ['scan', 'date', path])
    assert result.exit_code == 0
    assert result.output == expected_output
