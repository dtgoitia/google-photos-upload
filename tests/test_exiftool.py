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
    expected_result = "2019-01-01 08:50:26"

    actual_result = read_datetime("IMG_20190202_184442_353.jpg")

    assert actual_result == expected_result


def test_read_date_with_real_exiftool(tmp_real_img):
    expected_result = "2019-02-02 18:44:43"

    actual_result = read_datetime(tmp_real_img)

    assert actual_result == expected_result


def test_write_date(exiftool_mocked, tmp_real_img):
    pass
