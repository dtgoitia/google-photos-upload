import click

from gpy.cli.meta import meta_group
from gpy.cli.scan import scan_group


@click.group()
def gpy_cli() -> None:
    pass


gpy_cli.add_command(meta_group)
gpy_cli.add_command(scan_group)
