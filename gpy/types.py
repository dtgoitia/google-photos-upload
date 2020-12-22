from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

import attr


@attr.s(auto_attribs=True, frozen=True)
class GpsCoordinates:
    longitude: Decimal
    latitude: Decimal

    @property
    def as_exif(self) -> Any:
        # What format do I use for writing GPS coordinates?
        # https://exiftool.org/faq.html#Q14
        raise NotImplementedError()


@attr.s(auto_attribs=True, frozen=True)
class Report:
    path: Path

    filename_date: Optional[datetime] = None
    metadata_date: Optional[datetime] = None
    gps: Optional[GpsCoordinates] = None

    @property
    def dates_match(self) -> bool:
        return _compare_dates(self.filename_date, self.metadata_date)


def _compare_dates(a: Optional[datetime], b: Optional[datetime]) -> bool:
    if not (a and b):
        return False

    return a == b
