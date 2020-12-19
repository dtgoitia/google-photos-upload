"""This module contains the fixtures to create one or more temporary files for
the tests.
"""
import os
from typing import Callable, List

import pytest
from py._path.local import LocalPath

TmpFileCreator = Callable[[str], str]


@pytest.fixture
def create_tmp_file(tmpdir: LocalPath) -> TmpFileCreator:
    """Return function to temporary copy a given file for tests.

    The function makes a copy with the passed file name (file_name) into
    the temporary testing directory. The source file needs to be within the
    'tests/static/' directory, in order to be copied. The temporary test
    directory is created before and removed after every test. The file is
    copied as-is, preserving any metadata the file might contain.
    """

    def result(file_name: str) -> str:
        """."""
        source = os.path.join(os.getcwd(), "tests", "statics", file_name)
        with open(source, "rb") as file:
            content = file.read()
            tmpdir.join(file_name).write_binary(content)
        return os.path.join(tmpdir.dirname, tmpdir.basename, file_name)

    return result


@pytest.fixture
def tmp_real_img(create_tmp_file: TmpFileCreator) -> str:
    """Copy an image to the temporary testing directory.

    This image is a real file which contain origina metadata, preserved without
    any modification or deletion.
    """
    return create_tmp_file("IMG_20190202_184442_353.jpg")


@pytest.fixture
def tmp_real_vid(create_tmp_file: TmpFileCreator) -> str:
    """Copy a video to the temporary testing directory.

    This video is a real files which contain origina metadata, preserved
    without any modification or deletion.
    """
    return create_tmp_file("VID_20190202_184513_634.mp4")


@pytest.fixture
def tmp_real_files(create_tmp_file: TmpFileCreator) -> List[str]:
    """Copy the static files over to the temporary testing directory.

    The static files are real images which contain origina metadata, preserved
    without any modification or deletion.
    """
    files_name = (
        "IMG_20190202_184442_353.jpg",
        "IMG_20190202_184449_766.jpg",
        "IMG_20190202_184520_656.jpg",
        "VID_20190202_184425_556.mp4",
        "VID_20190202_184513_634.mp4",
    )
    return [create_tmp_file(file) for file in files_name]
