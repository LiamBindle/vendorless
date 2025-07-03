import click
import importlib.resources
from cookiecutter.main import cookiecutter
import tempfile

from pathlib import Path

import runpy
import subprocess
from rich.console import Console
import shutil

import re
import os

from vendorless.core.service_template import ServiceTemplate

@click.group()
def cli():
    pass



@cli.group()
@click.argument('stack', type=click.STRING) # foo.py for local, package.module for package
@click.option('-s', '--secrets', type=click.Path(exists=True, file_okay=False, dir_okay=True), default=None, help='path to secrets dir')
def build(stack: str, secrets):
    """
    Build a stack.

    STACK is the module (.py file or package module) that defines the stack.
    """
    # if stack is local file -> build locally
    if stack.endswith('.py'):
        runpy.run_path(stack)
    else:
        runpy.run_module(stack)
    ServiceTemplate.render_stack('output')


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
def pkg():
    pass

@pkg.command()
@click.option('-o', '--output-dir', type=click.Path(exists=True, file_okay=False, dir_okay=True), default='.', help='path to secrets dir')
def new(output_dir: str):
    """
    Create a new package. 
    """
    click.echo("Initializing new package.")
    templates_path = importlib.resources.files('vendorless.core.templates')
    cookiecutter(str(templates_path / 'package'), output_dir=output_dir)
    click.echo("New package initialized.")


def run_command(*command: str, return_stdout: bool=False, input: str=None, cwd=None, env=None) -> str:
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
        cwd=cwd,
        env=env,
    )

    if not return_stdout:
        if input:
            process.stdin.write(input)
            process.stdin.flush()
            process.stdin.close()
            
        console = Console()
        with process.stdout:
            for line in iter(process.stdout.readline, ""):
                console.print(line, end="")
        process.wait()
        if process.returncode != 0:
            raise RuntimeError()
        return ""
    else:
        stdout, stderr = process.communicate()
        return stdout


@pkg.command()
def docs_serve():
    run_command('mkdocs', 'serve')

@pkg.command()
def docs_build():
    run_command('mkdocs', 'build', '-d', 'out/docs')


@pkg.command()
def test():
    run_command('pytest')


def extract_blocks(filepath: str, block: str):
    pattern = re.compile(fr"```{block} *\n(.*?)```", flags=re.MULTILINE | re.DOTALL)
    with open(filepath, 'r', encoding='utf-8') as f:
        matches = pattern.finditer(f.read())

    blocks = ''
    for match in matches:
        blocks += ''.join(match.groups())
    return blocks

@pkg.command()
@click.argument('filepath', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('-t', '--temp-dir', is_flag=True)
def docs_run(filepath: str, temp_dir: bool):

    bash_script = extract_blocks(filepath=filepath, block="console")
    bash_script = ''.join(l.removeprefix("$").strip(' ') for l in bash_script.splitlines(keepends=True) if l.startswith("$"))


    input = extract_blocks(filepath=filepath, block="salt")
    input = ''.join(l.split(':', maxsplit=1)[1].strip(' ') for l in input.splitlines(keepends=True))

    tmpdir = tempfile.TemporaryDirectory(prefix='vendorless.core.', delete=not temp_dir)

    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)  # don't modify the current environment

    if not temp_dir:
        run_command(
            'bash', '-c', f"set -x\n{bash_script}",
            input=input,
            env=env,
        )
    else:
        with tmpdir:
            run_command(
                'bash', '-c', f"set -x\n{bash_script}",
                input=input,
                cwd=tmpdir.name,
                env=env,
            )
            shutil.rmtree(tmpdir.name)
        
    
@pkg.command()
def publish():
    run_command('poetry', 'build')
    run_command('poetry', 'publish')



# install and run 

# @click.group()
