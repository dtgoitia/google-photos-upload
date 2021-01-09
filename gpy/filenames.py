"""This module contains the logic to parse dates from file names."""
import datetime
import re
from typing import Optional


def parse_datetime(file_name: str) -> Optional[datetime.datetime]:
    """Return timestamp from file name."""
    case_1 = _parse_case_a(file_name)
    if case_1:
        return case_1
    case_2 = _parse_case_b(file_name)
    if case_2:
        return case_2
    case_3 = _parse_case_c(file_name)
    if case_3:
        return case_3
    case_4 = _parse_case_d(file_name)
    if case_4:
        return case_4

    return None


def _parse_case_a(file_name: str) -> Optional[datetime.datetime]:
    """Return timestamp from file name.

    IMG_YYYYMMDD_hhmmss_XXX.jpg, where XXX is a counter
    """
    pattern = r"IMG_([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2})([0-9]{2})([0-9]{2})_[0-9]{3}.jpg"
    matches = re.match(pattern, file_name)
    if matches is None:
        return None
    year = int(matches.group(1))
    month = int(matches.group(2))
    day = int(matches.group(3))
    h = int(matches.group(4))
    m = int(matches.group(5))
    s = int(matches.group(6))
    return datetime.datetime(year, month, day, h, m, s)


def _parse_case_b(file_name: str) -> Optional[datetime.datetime]:
    """Return timestamp from file name.

    VID_YYYYMMDD_hhmmss_XXX.mp4, where XXX is a counter
    """
    pattern = r"VID_([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2})([0-9]{2})([0-9]{2})_[0-9]{3}.mp4"
    matches = re.match(pattern, file_name)
    if matches is None:
        return None
    year = int(matches.group(1))
    month = int(matches.group(2))
    day = int(matches.group(3))
    h = int(matches.group(4))
    m = int(matches.group(5))
    s = int(matches.group(6))
    return datetime.datetime(year, month, day, h, m, s)


def _parse_case_c(file_name: str) -> Optional[datetime.datetime]:
    """Return timestamp from file name.

    IMG-YYYYMMDD-WAXXXX.jpeg, where XXXX is a counter
    """
    pattern = r"IMG-([0-9]{4})([0-9]{2})([0-9]{2})-WA[0-9]{4}.jpeg"
    matches = re.match(pattern, file_name)
    if matches is None:
        return None
    year = int(matches.group(1))
    month = int(matches.group(2))
    day = int(matches.group(3))
    return datetime.datetime(year, month, day)


def _parse_case_d(file_name: str) -> Optional[datetime.datetime]:
    """Return timestamp from file name.

    VID-YYYYMMDD-WAXXXX.mp4, where XXXX is a counter
    """
    pattern = r"VID-([0-9]{4})([0-9]{2})([0-9]{2})-WA[0-9]{4}.mp4"
    matches = re.match(pattern, file_name)
    if matches is None:
        return None
    year = int(matches.group(1))
    month = int(matches.group(2))
    day = int(matches.group(3))
    return datetime.datetime(year, month, day)
