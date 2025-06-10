import click
import importlib.resources
from cookiecutter.main import cookiecutter

from pathlib import Path

import runpy
import subprocess
from rich.console import Console

from vendorless.core.blueprints import Blueprint

@click.group()
def cli():
    pass

@cli.command()
def new():
    """
    Create a new package. 
    """
    click.echo("Initializing new package.")
    templates_path = importlib.resources.files('vendorless.core.templates')
    cookiecutter(str(templates_path / 'package'))
    click.echo("New package initialized.")


@cli.group()
@click.argument('stack', type=click.STRING) # foo.py for local, package.module for package
@click.option('-s', '--secrets', type=click.Path(exists=True, file_okay=False, dir_okay=True), default=None, help='path to secrets dir')
def build(stack: str, secrets_dir):
    """
    Build a stack.

    STACK is the module (.py file or package module) that defines the stack.
    """
    # if stack is local file -> build locally
    if stack.endswith('.py'):
        runpy.run_path(stack)
    else:
        runpy.run_module(stack)
    Blueprint.render_stack('output')


@cli.group()
@click.argument('stack', type=click.STRING)
def run(stack):
    """
    Run a stack.

    STACK is the module (.py file or package module) that defines the stack.
    """
    # if stack is local file -> build locally
    pass

@cli.group()
def dev():
    pass


def run_command(*command: str):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
    )
    console = Console()
    with process.stdout:
        for line in iter(process.stdout.readline, ""):
            console.print(line, end="")
    process.wait()

@dev.command()
def docs_serve():
    run_command('poetry', 'run', 'mkdocs', 'serve')

@dev.command()
def docs_build():
    run_command('poetry', 'run', 'mkdocs', 'build', '-d', f'out/docs')


# install and run 

# @click.group()
