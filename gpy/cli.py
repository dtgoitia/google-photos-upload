import click


@click.group()
def main():
    """Entry point."""
    click.echo('main')
    # pass


@main.command()
def boo():
    """Shout 'Boo!' command description."""
    click.echo('boo')
