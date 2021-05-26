import datetime
import logging
from pathlib import Path

import click
import pytz

from gpy.config import UPLOADED_MEDIA_INFO_DIR
from gpy.filesystem import write_json
from gpy.gphotos import GooglePhotosClient
from gpy.types import JsonDict, structure, unstructure

logger = logging.getLogger(__name__)


@click.command(name="fetch_uploaded_media_info")
# @click.argument("path", type=click.Path(exists=True))
def fetch_uploaded_media_info_command() -> None:
    """Get a JSON with a list of all the media items in Google Photos.

    Only media items between 1990-01-01 and 2005-01-01 will be returned.
    """
    fetch_uploaded_media_info_between_dates(
        start=datetime.datetime(1990, 1, 1),
        end=datetime.datetime(2005, 1, 1),
    )


def build_path(start: datetime.date, end: datetime.date) -> Path:
    formatted_start = start.strftime("%Y-%m-%d")
    formatted_end = end.strftime("%Y-%m-%d")
    now = datetime.datetime.now().replace(microsecond=0).isoformat()

    filename = f"uploaded_media_info__{formatted_start}_{formatted_end}__{now}.json"

    path = UPLOADED_MEDIA_INFO_DIR / filename

    return path


def fetch_uploaded_media_info_between_dates(
    start: datetime.datetime,
    end: datetime.datetime,
) -> Path:
    client = GooglePhotosClient()
    client.start_session()

    output_path = build_path(start=start, end=end)

    media_items = list(client.search_media_items(start=start, end=end))
    json_items = unstructure(media_items)

    content = list(json_items)

    write_json(output_path, content=content)
    logger.info(
        "Data retrieved from GPhotos about which media is uploaded has been stored at"
        f" {output_path}"
    )

    return output_path
