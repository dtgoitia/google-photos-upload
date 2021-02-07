from datetime import datetime
from pathlib import Path

import pytest

from gpy.exiftool.client import ExifToolError, parse_datetime, read_datetime


@pytest.fixture
def exiftool_mocked(mocker):
    return mocker.patch("subprocess.run")


class MockSubprocess:

    returncode = 0
    stdout = b"REPLACE_WITH_DESIRED_STDOUT"


# -----------------------------------------------------------------------------
# Tests


@pytest.mark.parametrize(
    ("stdout", "expected_result"),
    (
        # pytest.param(
        #     ": 2019:01:01 08:50:26 \n",
        #     datetime(2019, 1, 1, 8, 50, 25),
        #     id="not_sure_when_this_happens",
        # ),
        pytest.param(
            (
                "some random text above the dates\n"
                "Date/Time Original              : 2019:02:02 18:44:43\n"
                "Create Date                     : 2019:02:02 18:44:44\n"
                "Modify Date                     : 2019:02:02 18:44:45\n"
            ),
            datetime(2019, 2, 2, 18, 44, 43),
            id="full_blown",
        ),
    ),
)
def test_parse_datetime(stdout, expected_result):
    result = parse_datetime(stdout)
    assert result == expected_result


@pytest.mark.parametrize(
    ("stdout", "error_msg"),
    (
        pytest.param(
            b"",
            "Output is empty",
            id="empty_output_or_file_without_metadata",
        ),
        pytest.param(
            b"this is a very cool\nbut multiline output",
            (
                "No supported timestamps found in the following output:\n"
                "  > this is a very cool\n"
                "  > but multiline output"
            ),
            id="no_matching_output",
        ),
        pytest.param(
            b"unsupported output: 2019:01:01 08:50:26 \n",
            (
                "No supported timestamps found in the following output:\n"
                "  > unsupported output: 2019:01:01 08:50:26 \n"
            ),
            id="unsupported_output",
        ),
    ),
)
def test_read_datetime_raises_if(exiftool_mocked, stdout, error_msg):
    exiftool_mocked.return_value = MockSubprocess()
    exiftool_mocked.return_value.stdout = stdout
    path = Path("blah.jpg")

    with pytest.raises(ExifToolError) as e:
        read_datetime(path)

    exc = e.value

    assert exc.args == (error_msg,)


@pytest.mark.skip(reason="not implemented yet")
def test_write_date(exiftool_mocked, tmp_real_img):
    pass
