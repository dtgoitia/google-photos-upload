import re
from datetime import datetime
from typing import Optional


def try_to_parse_date(text: Optional[str]) -> Optional[datetime]:
    """Parse the date with multiple formats and return the first match."""
    if not text:
        return None
    case_1 = try_to_parse_date_1(text)
    if case_1:
        return case_1
    case_2 = try_to_parse_date_2(text)
    if case_2:
        return case_2
    return None


def try_to_parse_date_1(text: str) -> Optional[datetime]:
    """Try to parse text to date (2019-02-02 18:45:13)."""
    pattern = r"([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2})"
    matches = re.match(pattern, text)
    if matches is None:
        return None
    year = int(matches.group(1))
    month = int(matches.group(2))
    day = int(matches.group(3))
    h = int(matches.group(4))
    m = int(matches.group(5))
    s = int(matches.group(6))
    return datetime(year, month, day, h, m, s)


def try_to_parse_date_2(text: str) -> Optional[datetime]:
    """Try to parse text to date (2019-02-02 18:45:13.00+00:00)."""
    pattern = r"([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2}).[0-9]{2}\+[0-9]{2}:[0-9]{2}"
    matches = re.match(pattern, text)
    if matches is None:
        return None
    year = int(matches.group(1))
    month = int(matches.group(2))
    day = int(matches.group(3))
    h = int(matches.group(4))
    m = int(matches.group(5))
    s = int(matches.group(6))
    return datetime(year, month, day, h, m, s)
