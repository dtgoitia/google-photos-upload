import logging
import sys

import click

from gpy.cli.meta import meta_group
from gpy.cli.scan import scan_group
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
