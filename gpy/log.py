from typing import Optional

import click

from gpy.types import Report


def print_report(report: Report) -> None:
    """Print on screen a report dictionary."""
    if not report.dates_match:
        log("    metadata date and file timestamp don't match")


def log(s: str, fg: Optional[str] = None) -> None:
    """Log with colour."""
    click.echo(click.style(s, fg=fg))


# TODO:
# Add more regex patterns to recognize more image file names and ensure the date
# Create one command that will:
#   1. Scan all images or videos in the directory
#   2. Try to parse the filename to extract timestamp.
#   3. Look data and geolocation metadata in the files.
#   4. Report:
#        - Filename and metadata match, +GPS -> OK
#        - If no GPS metadata -> Add '_nogps' at the end of the filename
#        - Filename and metadata don't match ->
