import click
from cookiecutter.main import cookiecutter
import importlib.resources


# vl (verb) (noun)

@click.group()
def cli():
    """VL CLI tool"""
    pass

@click.group()
def new():
    """Create a new blueprint or stack."""
    pass

@new.command()
def module():
    """Create a new module."""
    click.echo("Initializing new module.")
    templates_path = importlib.resources.files('vendorless.templates')
    print(templates_path)
    cookiecutter(str(templates_path / 'module'))
    click.echo("New module initialized.")

@new.command()
@click.argument("name")
def stack(name):
    """Create a new stack."""
    click.echo(f"New stack '{name}' created.")

@click.command()
def render():
    """Render the project."""
    click.echo("Project rendered.")

cli.add_command(new)
cli.add_command(render)

if __name__ == '__main__':
    cli()