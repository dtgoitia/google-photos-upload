from pathlib import Path

import pytest

from gpy.exiftool import read_datetime


@pytest.fixture
def exiftool_mocked(mocker):
    return mocker.patch("subprocess.run")


class MockSubprocess:

    returncode = 0
    stdout = b"REPLACE_WITH_DESIRED_STDOUT"


# -----------------------------------------------------------------------------
# Tests


def test_read_date_with_mocked_exiftool(exiftool_mocked):
    exiftool_mocked.return_value = MockSubprocess()
    exiftool_mocked.return_value.stdout = b": 2019:01:01 08:50:26 \n"
    dumb_path = Path("IMG_20190202_184442_353.jpg")

    result = read_datetime(dumb_path)

    assert result == "2019-01-01 08:50:26"


def test_handle_file_without_date(exiftool_mocked):
    exiftool_mocked.return_value = MockSubprocess()
    exiftool_mocked.return_value.stdout = b""
    dumb_path = Path("IMG_20190202_184442_353.jpg")

    result = read_datetime(dumb_path)

    assert result is None


def test_read_date_with_real_exiftool(tmp_real_img):

    result = read_datetime(tmp_real_img)

    assert result == "2019-02-02 18:44:43"


@pytest.mark.skip(reason="not implemented yet")
def test_write_date(exiftool_mocked, tmp_real_img):
    pass
