import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class FfmpegError(Exception):
    ...


def path_to_mp4(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)

    output_path = path.parent / f"{path.stem}.mp4"
    if output_path.exists():
        raise Exception(
            f"{output_path} already exists, delete it to carry on, if that is what"
            " you want"
        )

    cmd = f'ffmpeg -i "{path}" "{output_path}"'

    logger.info(f"Converting {path} to mp4")
    completed_process = subprocess.run(cmd, capture_output=True, shell=True)

    if completed_process.returncode != 0:
        error_message = completed_process.stderr.decode("utf-8").strip("\n")
        logger.error(error_message)
        raise FfmpegError(error_message)
