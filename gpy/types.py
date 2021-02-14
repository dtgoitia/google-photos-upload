import logging
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

import attr
import cattr

converter = cattr.Converter()
structure = converter.structure
unstructure = converter.unstructure

logger = logging.getLogger(__name__)


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
class Report:  # TODO: rename Report --> MediaMetadata
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


def _compare_dates(a: Optional[datetime], b: Optional[datetime]) -> bool:
    if not (a and b):
        return False

    return a == b


def print_report(report: Report) -> None:
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
