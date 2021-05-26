from pathlib import Path
from zoneinfo import ZoneInfo

import pytz

SPAIN = ZoneInfo("Europe/Madrid")
UK = ZoneInfo("Europe/London")

DEFAULT_ZONEINFO = SPAIN

DEFAULT_TZ = pytz.timezone(DEFAULT_ZONEINFO.key)

REPORTS_DIR = Path("reports")
# TODO: add a file to record which state is the last
# no need for this
# each time you run a new report, you should dump a new file
# REPORTS_STATE_PATH = REPORTS_DIR / "last_state"
UPLOADED_MEDIA_INFO_DIR = REPORTS_DIR / "uploaded-in-gphotos"
LOCAL_MEDIA_INFO_DIR = REPORTS_DIR / "local-dates"
AGGREGATED_MEDIA_INFO_DIR = REPORTS_DIR / "aggregated"
MEDIA_DIR = Path("to_backup_in_gphotos")
