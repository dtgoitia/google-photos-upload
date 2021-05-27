import logging
import sys
from distutils.command.upload import upload
from pathlib import Path

from gpy.gphotos import GooglePhotosClient, upload_media
from gpy.log import get_log_format, get_logs_output_path


def upload_single_file(path: Path) -> None:
    client = GooglePhotosClient()
    client.start_session()
    upload_media(session=client._session, path=path)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    logs_path = get_logs_output_path()
    log_format = get_log_format()
    logging.basicConfig(filename=logs_path, format=log_format, level=logging.DEBUG)

    try:
        uri = sys.argv[1]
    except IndexError:
        print("Please specify the path of the file to upload :)")
        exit(1)
    path = Path(uri)

    logger.info(f"Uploading {path} to GPhotos")
    upload_single_file(path)
    logger.info(f"Finished uploading {path} to GPhotos")
