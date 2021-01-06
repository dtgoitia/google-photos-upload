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


DATE_A_REGEX = re.compile(
    r"([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2})"
)
DATE_B_REGEX = re.compile(
    r"([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2}).[0-9]{2}\+[0-9]{2}:[0-9]{2}"
)


def try_to_parse_date_1(text: str) -> Optional[datetime]:
    """Try to parse text to date (2019-02-02 18:45:13)."""
    breakpoint()
    matches = DATE_A_REGEX.match(text)

    if not matches:
        return

    year, month, day, hour, minute, second = matches.groups()

    return datetime(
        year=int(year),
        month=int(month),
        day=int(day),
        hour=int(hour),
        minute=int(minute),
        second=int(second),
    )


def try_to_parse_date_2(text: str) -> Optional[datetime]:
    """Try to parse text to date (2019-02-02 18:45:13.00+00:00)."""
    matches = DATE_B_REGEX.match(text)

    if not matches:
        return

    year, month, day, hour, minute, second = matches.groups()

    return datetime(
        year=int(year),
        month=int(month),
        day=int(day),
        hour=int(hour),
        minute=int(minute),
        second=int(second),
    )
