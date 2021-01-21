from pathlib import Path, PosixPath

import pytest

from gpy.filesystem import get_paths_recursive, is_supported


def mkdir(path: Path, dir_name: str) -> Path:
    dir = path / dir_name
    dir.mkdir()
    return dir


@pytest.fixture
def mock_dir(tmp_path: PosixPath) -> Path:
    test_dir = Path(tmp_path)
    (test_dir / "file_1.jpg").write_text("file content 1\n")
    (test_dir / "file_2.png").write_text("file content 2\n")
    (test_dir / "file_3.3gp").write_text("file content 3\n")
    (test_dir / "file_4.mp3").write_text("file content 4\n")
    subdir = mkdir(test_dir, "directory_1")
    (subdir / "file_5.wav").write_text("file content 5\n")
    (subdir / "file_6.mp4").write_text("file content 6\n")

    return test_dir


@pytest.mark.parametrize(
    ("extension"),
    [
        "jpg",
        "png",
        "mp4",
        "3gp",
    ],
)
def test_supported_files(extension):
    path = Path(f"file/absolute/path.{extension}")
    assert is_supported(path) is True

    path = Path(f"file/absolute/path.{extension.upper()}")
    assert is_supported(path) is True


@pytest.mark.parametrize(
    ("extension"),
    [
        "gif",
        "GIF",
    ],
)
def test_unsupported_files(extension):
    path = Path(f"file/absolute/path.{extension}")
    assert is_supported(path) is False

    path = Path(f"file/absolute/path.{extension.upper()}")
    assert is_supported(path) is False


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
