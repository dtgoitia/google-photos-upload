import click
from gpy.oauth import get_token


@click.group()
def main():
    """Entry point."""
    # click.echo('main')
    pass


@main.command()
def auth():
    """Get access token for Google API."""
    result = get_token()
    print(f'result = {result}')
