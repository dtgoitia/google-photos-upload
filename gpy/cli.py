import click
from gpy.oauth import get_token


@click.group()
def main():
    """Entry point."""
    click.echo('main')
    # pass


@main.command()
def boo():
    """Shout 'Boo!' command description."""
    click.echo('boo')
    result = get_token()
    print(f'result = {result}')

