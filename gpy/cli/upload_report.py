"""
escanea todos los archivos
crea report
subelos a gsheet
"""

import logging
from pathlib import Path

import click
import gspread

from gpy.filesystem import read_reports
from gpy.google_sheet import FileReport, fetch_worksheet, merge, upload_worksheet

logger = logging.getLogger(__name__)


@click.command(name="upload_report")
@click.argument("path", type=click.Path(exists=True))
def upload_report_command(path: str) -> None:
    """Upload scan-report to Google Spreadsheet."""
    upload_report(report_path=Path(path))


def upload_report(report_path: Path) -> None:
    logger.info(f"Reading reports from {report_path}")
    reports = read_reports(report_path)

    file_reports = [
        FileReport(
            path=report.path,
            dates_match=report.dates_match,
            has_ghotos_timestamp=report.has_google_date,
            uploaded=False,
        )
        for report in reports
    ]

    logger.info("Authenticating with Google Spreadsheet API...")
    gc = gspread.oauth()

    spreadsheet_name = "Photo backup tracker"
    sh = gc.open(spreadsheet_name)

    logger.info(f"Fetching data from the {spreadsheet_name!r} spreadsheet...")
    gsheet = fetch_worksheet(sh)

    logger.info("Merging report data with the spreadsheet...")
    updated_gsheet = merge(gsheet, file_reports)

    logger.info("Uploading updated data to the spreadsheet...")
    upload_worksheet(sh, updated_gsheet)
    logger.info("Report upload successfuly completed")
