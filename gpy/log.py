import datetime
import logging
from logging import LogRecord
from pathlib import Path

import colored
from colored import stylize

logger = logging.getLogger(__name__)


class ConditionalFormatter(logging.Formatter):
    # https://stackoverflow.com/questions/1343227/can-pythons-logging-format-be-modified-depending-on-the-message-log-level
    # https://github.com/pygments/pygments
    def format(self, record: LogRecord) -> str:
        message = record.msg

        if record.levelno == logging.DEBUG:
            coloured = stylize(message, colored.fg("dark_gray"))
            return coloured
        else:
            return message


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


def get_logs_output_path() -> Path:
    today = datetime.date.today().isoformat()
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    logs_path = logs_dir / f"{today}.log"
    return logs_path


def get_log_format() -> str:
    # https://docs.python.org/3/library/logging.html#logrecord-attributes
    return "%(asctime)s:%(levelname)s:%(filename)s:%(lineno)d:%(message)s"
