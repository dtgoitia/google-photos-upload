"""This module contains the fixtures to create one or more temporary files for
the tests.
"""
import shutil
from pathlib import Path, PosixPath
from typing import Callable, List

import pytest

TmpFileCreator = Callable[[str], Path]


@pytest.fixture
def fixtures_dir() -> Path:
    return Path.cwd() / "tests" / "statics"


@pytest.fixture
def create_tmp_file(tmp_path: PosixPath, fixtures_dir: Path) -> TmpFileCreator:
    """Return function to temporary copy a given file for tests.

    The function makes a copy with the passed file name (file_name) into
    the temporary testing directory. The source file needs to be within the
    'tests/static/' directory, in order to be copied. The temporary test
    directory is created before and removed after every test. The file is
    copied as-is, preserving any metadata the file might contain.
    """

    def file_copier(file_name: str) -> Path:
        """."""
        source_path = fixtures_dir / file_name
        new_fixture_path = tmp_path / file_name

        shutil.copy(src=source_path, dst=new_fixture_path)

        return new_fixture_path

    return file_copier


@pytest.fixture
def tmp_real_img(create_tmp_file: TmpFileCreator) -> Path:
    """Copy an image to the temporary testing directory.

    This image is a real file which contain origina metadata, preserved without
    any modification or deletion.
    """
    return create_tmp_file("IMG_20190202_184442_353.jpg")


@pytest.fixture
def tmp_real_vid(create_tmp_file: TmpFileCreator) -> Path:
    """Copy a video to the temporary testing directory.

    This video is a real files which contain origina metadata, preserved
    without any modification or deletion.
    """
    return create_tmp_file("VID_20190202_184513_634.mp4")


@pytest.fixture
def tmp_real_files(create_tmp_file: TmpFileCreator) -> List[Path]:
    """Copy the static files over to the temporary testing directory.

    The static files are real images which contain origina metadata, preserved
    without any modification or deletion.
    """
    file_names = (
        "IMG_20190202_184442_353.jpg",
        "IMG_20190202_184449_766.jpg",
        "IMG_20190202_184520_656.jpg",
        "VID_20190202_184425_556.mp4",
        "VID_20190202_184513_634.mp4",
    )
    paths = [create_tmp_file(file_name) for file_name in file_names]
    return paths
