import logging
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Optional

import attr
import cattr

converter = cattr.Converter()
structure = converter.structure
unstructure = converter.unstructure

JsonDict = Dict[str, Any]


logger = logging.getLogger(__name__)

Scope = str
Url = str
MimeType = str  # "image/jpeg"
FileId = str  #


def structure_path(path: str, _: Any) -> Path:
    return Path(path)


def unstructure_path(path: Path) -> str:
    return str(path)


converter.register_unstructure_hook(Path, unstructure_path)
converter.register_structure_hook(Path, structure_path)


@attr.s(auto_attribs=True, frozen=True)
class GpsCoordinates:
    longitude: Decimal
    latitude: Decimal

    @property
    def as_exif(self) -> Any:
        # What format do I use for writing GPS coordinates?
        # https://exiftool.org/faq.html#Q14
        raise NotImplementedError()


def _format_datetime(d: datetime) -> str:
    milliseconds = round(d.microsecond / 1000)

    result = f'{d.strftime("%Y-%m-%d %H:%M:%S")}.{milliseconds:03}'
    return result


def structure_datetime(d: str, _: Any) -> datetime:
    return datetime.fromisoformat(d)


def unstructure_datetime(d: datetime) -> str:
    return d.isoformat()


converter.register_structure_hook(datetime, structure_datetime)
converter.register_unstructure_hook(datetime, unstructure_datetime)


@attr.s(auto_attribs=True, frozen=True)
class FileDateReport:
    path: Path
    filename_date: Optional[datetime] = None
    metadata_date: Optional[datetime] = None
    google_date: Optional[datetime] = None
    gps: Optional[GpsCoordinates] = None

    @property
    def dates_match(self) -> bool:
        return _compare_dates(self.filename_date, self.metadata_date)

    @property
    def fmt_filename_date(self) -> str:
        assert self.filename_date
        return _format_datetime(self.filename_date)

    @property
    def fmt_metadata_date(self) -> str:
        assert self.metadata_date
        return _format_datetime(self.metadata_date)

    @property
    def has_google_date(self) -> bool:
        return self.google_date is not None

    @property
    def is_ready_to_upload(self) -> bool:
        if self.has_google_date is False:
            return False

        return self.filename_date is None


def _compare_dates(a: Optional[datetime], b: Optional[datetime]) -> bool:
    if not (a and b):
        return False

    return a == b


def print_report(report: FileDateReport) -> None:
    """Print on screen a report dictionary."""

    if report.filename_date is None and report.metadata_date is None:
        logger.info("  timestamp not found in metadata or filename")
    elif report.filename_date is not None and report.metadata_date is None:
        logger.info("  timestamp found in filename, but not in metadata")
    elif report.filename_date is None and report.metadata_date is not None:
        logger.debug("  OK: timestamp found in metadata, but not in filename")
    elif not report.dates_match:
        logger.info(
            "  metadata date and file timestamp don't match\n"
            f"    > metadata: {report.fmt_metadata_date}\n"
            f"    > filename: {report.fmt_filename_date}"
        )
    elif report.filename_date == report.metadata_date:
        logger.debug("    OK: matching timestamp found in filename and in metadata")
    else:
        raise NotImplementedError("An unexpected case was reached!")


@attr.s(auto_attribs=True, frozen=True)
class MediaMetadata:
    creation_time: datetime
    width: int
    height: int
    photo: Optional[JsonDict] = None


def structure_media_metadata(raw: JsonDict, _: Any) -> MediaMetadata:
    return MediaMetadata(
        creation_time=structure_datetime(raw["creationTime"], None),
        width=int(raw["width"]),
        height=int(raw["height"]),
        photo=raw.get("photo"),
    )


def unstructure_media_metadata(media_metadata: MediaMetadata) -> JsonDict:
    return {
        "creationTime": unstructure_datetime(media_metadata.creation_time),
        "width": media_metadata.width,
        "height": media_metadata.height,
        "photo": media_metadata.photo,
    }


converter.register_structure_hook(MediaMetadata, structure_media_metadata)
converter.register_unstructure_hook(MediaMetadata, unstructure_media_metadata)


@attr.s(auto_attribs=True, frozen=True)
class MediaItem:
    # https://developers.google.com/photos/library/reference/rest/v1/mediaItems#MediaItem
    id: str
    product_url: Url
    base_url: Url
    mime_type: MimeType
    # https://developers.google.com/photos/library/reference/rest/v1/mediaItems#MediaMetadata
    media_metadata: MediaMetadata
    # https://developers.google.com/photos/library/reference/rest/v1/mediaItems#ContributorInfo
    filename: str
    contributor_info: Optional[JsonDict] = None
    description: Optional[str] = None

    # def to_json(self) -> JsonDict:
    #     if self.contributor_info:
    #         contributor_info = self.contributor_info.to_json()
    #     else:
    #         contributor_info = None

    #     return {
    #         "id": self.id,
    #         "productUrl": self.product_url,
    #         "baseUrl": self.base_url,
    #         "mimeType": self.mime_type,
    #         "mediaMetadata": self.media_metadata.to_json(),
    #         "filename": self.filename,
    #         "contributorInfo": contributor_info,
    #         "description": self.description,
    #     }


def structure_media_item(raw: JsonDict, _: Any) -> MediaItem:
    media_item = MediaItem(
        id=raw["id"],
        product_url=raw["productUrl"],
        base_url=raw["baseUrl"],
        mime_type=raw["mimeType"],
        media_metadata=structure_media_metadata(raw["mediaMetadata"], None),
        filename=raw["filename"],
    )
    return media_item


def unstructure_media_item(media_item: MediaItem) -> JsonDict:
    if media_item.contributor_info:
        contributor_info = media_item.contributor_info
    else:
        contributor_info = None

    return {
        "id": media_item.id,
        "productUrl": media_item.product_url,
        "baseUrl": media_item.base_url,
        "mimeType": media_item.mime_type,
        "mediaMetadata": unstructure_media_metadata(media_item.media_metadata),
        "filename": media_item.filename,
        "contributorInfo": contributor_info,
        "description": media_item.description,
    }


converter.register_structure_hook(MediaItem, structure_media_item)
converter.register_unstructure_hook(MediaItem, unstructure_media_item)
