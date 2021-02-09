import logging

import click

from gpy.cli.meta import meta_group
from gpy.cli.scan import scan_group


@click.group()
@click.option("--debug", is_flag=True, default=False, help="debugging mode")
def gpy_cli(debug: bool) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level)


gpy_cli.add_command(meta_group)
gpy_cli.add_command(scan_group)
