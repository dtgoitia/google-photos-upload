import logging
import sys

import click

from gpy.cli.meta import meta_group
from gpy.cli.report_uploaded import fetch_uploaded_media_info_command
from gpy.cli.scan import scan_group
from gpy.cli.upload_report import upload_report_command
from gpy.log import ConditionalFormatter


@click.group()
@click.option("--debug", is_flag=True, default=False, help="debugging mode")
def gpy_cli(debug: bool) -> None:
    format = "%(message)s"
    level = logging.DEBUG if debug else logging.INFO

    conditional_formatter = ConditionalFormatter()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(conditional_formatter)

    logging.basicConfig(level=level, format=format, handlers=[handler])


gpy_cli.add_command(meta_group)
gpy_cli.add_command(scan_group)
gpy_cli.add_command(upload_report_command)
gpy_cli.add_command(fetch_uploaded_media_info_command)
