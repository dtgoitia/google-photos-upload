import datetime
import logging
import sys
from pathlib import Path

from gpy.exiftool import client as exiftool
from gpy.exiftool.client import ExifToolError
from gpy.log import get_log_format, get_logs_output_path

logger = logging.getLogger(__name__)


def add_metadata_to_single_file(path: Path, iso_timestamp: str) -> None:
    # # ISO format: 2005-09-14T10:07:08+02:00
    # ts = datetime.datetime.fromisoformat(input[:-7])
    # ts.astimezone(pytz.utc).astimezone(pytz.timezone("Europe/Madrid"))

    ts = datetime.datetime.fromisoformat(iso_timestamp)

    try:
        # Read XMP date (XMP supports timezone, EXIF doesn't):
        # exiftool -XMP:CreateDate path/to/my/media.jpg
        #
        # Read all EXIF dates:
        # exiftool -AllDates path/to/my/media.jpg
        if not path.exists:
            raise FileNotFoundError(path)
        exiftool.write_ts_raw(path, ts=ts, backup=True)
    except ExifToolError as exc:
        logger.warning(exc.args[0])


if __name__ == "__main__":

    logs_path = get_logs_output_path()
    log_format = get_log_format()
    logging.basicConfig(filename=logs_path, format=log_format, level=logging.DEBUG)

    try:
        uri = sys.argv[1]
    except IndexError:
        print("Please specify the path of the file to edit :)")
        exit(1)

    try:
        iso_timestamp = sys.argv[2]
    except IndexError:
        print("Please specify the date to add in ISO format: 2005-09-14T10:07:08+02:00")
        exit(1)

    path = Path(uri)

    logger.info(f"Editing metadata in {path}")
    add_metadata_to_single_file(path, iso_timestamp)
    logger.info(f"Finished editing metadata in {path}")
