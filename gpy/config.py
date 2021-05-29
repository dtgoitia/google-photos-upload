from pathlib import Path
from zoneinfo import ZoneInfo

import pytz

SPAIN_TZ_NAME = "Europe/Madrid"
UK_TZ_NAME = "Europe/London"
DEFAULT_TZ_NAME = SPAIN_TZ_NAME
DEFAULT_TZ = pytz.timezone(DEFAULT_TZ_NAME)

SPAIN = ZoneInfo(SPAIN_TZ_NAME)
UK = ZoneInfo(UK_TZ_NAME)
DEFAULT_ZONEINFO = SPAIN


REPORTS_DIR = Path("reports")
# TODO: add a file to record which state is the last
# no need for this
# each time you run a new report, you should dump a new file
# REPORTS_STATE_PATH = REPORTS_DIR / "last_state"
UPLOADED_MEDIA_INFO_DIR = REPORTS_DIR / "uploaded-in-gphotos"
LOCAL_MEDIA_INFO_DIR = REPORTS_DIR / "local-dates"
AGGREGATED_MEDIA_INFO_DIR = REPORTS_DIR / "aggregated"
MEDIA_DIR = Path("to_backup_in_gphotos")

TABLE_AS_STRING_PATH = Path("table_as_string.txt")
USE_LAST_REPORT_ON_REFRESH = False
USE_ACTIONS_IN_GSHEET = True
RECONCILE_DRY_RUN = False
