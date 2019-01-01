import click


@click.group()
def main():
    """Entry point."""
    # click.echo('main')
    pass


@main.command()
def meta():
    """Manage file metadata."""
    click.echo('meta!')
