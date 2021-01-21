from pathlib import Path
from typing import Iterator


def is_supported(path: Path) -> bool:
    return path.suffix.lower() in (".jpg", ".png", ".mp4", ".3gp")


def get_paths_recursive(*, root_path: Path) -> Iterator[Path]:
    """Yield absolute path of supported files under root_path.

    Refer to is_supported() for further information on supported files.
    """
    if root_path.is_file() and is_supported(root_path):
        yield root_path
    else:
        for path in sorted(root_path.rglob("*")):
            if path.is_file() and is_supported(path):
                yield path
