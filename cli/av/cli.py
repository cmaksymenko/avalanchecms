import click
from av.auth import login

@click.group()
def cli():
    """Avalanche CLI"""
    pass

cli.add_command(login)

if __name__ == '__main__':
    cli()
