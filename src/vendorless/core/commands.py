import click
import importlib.resources
from cookiecutter.main import cookiecutter
import tempfile

from pathlib import Path

import runpy
import subprocess
from rich.console import Console
import rich.prompt
from rich.table import Table
import rich.progress
import shutil

import re
import os
import sys
import importlib.metadata
import yaml
import re

from vendorless.core.parameters import ConfigurationParameter, Configuration
from vendorless.core.service_template import ServiceTemplate
from .utils import change_cwd

console = Console()

@click.group()
def cli():
    pass


def confirm(prompt: str, yes: bool):
    return yes or rich.prompt.Confirm.ask(prompt, console=console)

@cli.command()
@click.argument('blueprint', type=click.STRING)
@click.option('-c', '--config', type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path), default=None, help='path to YAML file with config')
@click.option('-cs', '--config-select', type=str, default=None, help='used to select the config from a key path in the YAML file')
@click.option('-o', '--output', type=click.Path(file_okay=False, dir_okay=True, path_type=Path), default=None, help='path to the output directory')
@click.option('-y', '--yes', is_flag=True, help='Answer yes to all prompts')
def render(blueprint: str, config: Path | None, config_select: str | None, output: Path | None, yes: bool):
    """
    Renders a blueprint to a stack.

    STACK is the module (.py file or package module) that defines the stack.
    """
    # Run the blueprint; Keep the objects in results alive - used for resolve and render

    console.print(f"Loading blueprint ([bold]{blueprint}[/bold])")
    if blueprint.endswith('.py'):
        blueprint_path = Path(blueprint)
        results = runpy.run_path(blueprint)
        default_output_dir_name = blueprint_path.stem
        blueprint = str(Path(blueprint).resolve())
    else:
        results = runpy.run_module(blueprint)
        default_output_dir_name = blueprint
    
    packages = [f"{p}" for p in set(sys.modules.keys()) if p.startswith('vendorless.') and len(p.split('.'))==2]
    packages = {p: importlib.metadata.version(p) for p in packages}
    
    if output is None:
        output = Path(default_output_dir_name)
    
    if output.exists():
        if not confirm("The stack already exists. Do you want to overwrite it?", yes):
            return

        existing_lock_file = output / 'vendorless-lock.yaml'
        if (config is None) and existing_lock_file.exists():
            if confirm(f"Do you want to load the stack's config?", yes):
                config = existing_lock_file
                config_select = 'Config'

            console.print("Checking package versions from lock file")
            with open(existing_lock_file, 'r') as f:
                previous_packages: dict = yaml.safe_load(f)['packages']
            
            packages_diff = []
            for p in set(packages) | set(previous_packages):
                if packages.get(p) == previous_packages.get(p):
                    continue
                packages_diff.append([
                    p,
                    f"+{packages[p]}" if p in packages else "",
                    f"-{previous_packages[p]}" if p in previous_packages else "",
                ])
            
            packages_diff.sort(key=lambda x: x[0])
            
            if packages_diff:
                table = Table(title="Package Differences")
                table.add_column("Package", justify="left", no_wrap=True)
                table.add_column("New Version", justify="center", style="green", no_wrap=True)
                table.add_column("Old Version", justify="center", style="red", no_wrap=True)
                for row in packages_diff:
                    table.add_row(*row)
                console.print(table)
                if not confirm("Package versions have changed. Do you want to continue?", yes):
                    return
    else:
        console.print(f"Creating output directory [bold]{str(output)}[/bold]")
        output.mkdir(parents=True, exist_ok=True)
    
    if config is not None:
        config = config.resolve()

    with change_cwd(output):
        # Load settings
        configuration = Configuration(config, config_select) 
        configuration.resolve()

        # Render the stack
        files_before = {str(file) for file in Path('.').iterdir() if file.is_file()}
        console.print("Rendering the stack")
        ServiceTemplate.render_stack()

        # Save a lock file
        console.print("Saving the lock file")
        lock_file = {
            'blueprint': blueprint,
            'configuration': configuration.dict(),
            'packages': packages,
        }
        with open('vendorless-lock.yaml', 'w') as f:
            yaml.safe_dump(lock_file, f)

        # clean if necessary
        files_after = {str(file) for file in Path('.').iterdir() if file.is_file()}
        leftover_files = files_before - files_after
        if leftover_files:
            console.print("The following files are leftovers from previous work:")
            for leftover in sorted(leftover_files):
                console.print(f" [red]-{leftover}[/red]")
            if confirm("Do you want to clean up these leftover files?", yes):
                for leftover in rich.progress.track(leftover_files, description="Cleaning up..."):
                    file_path = Path(leftover)
                    if file_path.is_file():  # Double check it's a file
                        file_path.unlink()


@cli.command()
@click.argument('stack', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option('-l', '--live', is_flag=True, help='Run the stack in the foreground')
def start(stack: Path, live: bool):
    """
    Starts a stack.
    """
    extra_args = []
    if not live:
        extra_args.append('-d')
    run_command('docker', 'compose', 'up', *extra_args, cwd=stack)

@cli.command()
@click.argument('stack', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option('-d', '--destroy', is_flag=True, help='Delete the volumes')
def stop(stack: Path, destroy):
    """
    Stop a stack.
    """
    extra_args = []
    if destroy:
        extra_args.append('-v')
    run_command('docker', 'compose', 'down', *extra_args, cwd=stack)

@cli.command()
@click.argument('stack', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
def status(stack: Path):
    """
    Check the status of a running stack.
    """

    stdout: str = run_command('docker', 'compose', 'ps', "-q", cwd=stack, return_stdout=True)
    
    container_ids: list[str] = stdout.split()

    stdout = run_command(
        'docker',
        'inspect',
        '--format={{ index .Config.Labels "com.docker.compose.service" }},{{.Id | printf "%.8s"}},{{.State.Status}},{{if .State.Health}}{{.State.Health.Status}}{{else}}n/a{{end}},{{.State.ExitCode}}',
        *container_ids,
        return_stdout=True,
        cwd=stack
    )
    
    pattern = re.compile(r'^([\w.-]+)\s*,\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*$', re.MULTILINE)
    matches = pattern.findall(stdout)
    table = Table(title='Service Statuses')
    table.add_column("Service", justify="left", no_wrap=True)
    table.add_column("Id", justify="center", no_wrap=True)
    table.add_column("Lifecycle", justify="center", no_wrap=True)
    table.add_column("Health", justify="center", no_wrap=True)

    def check_lifecycle_status(status: str, exit_code: str) -> int:
        if status == 'running':
            return 0
        elif status == 'exited':
            if exit_code == "0":
                # exited successfully -> good
                return 0
            else:
                # exited unsuccessfully -> bad
                return 2
        elif status in ['created', 'restarting', 'removing', 'paused']:
            return 1
        elif status in [
            'dead'
        ]:
            return 2
        else:
            raise ValueError(f'unexpected lifecycle status: {status}')
    
    def check_health_status(status: str) -> int:
        if status in ['healthy', 'n/a']:
            return 0
        elif status == 'starting':
            return 1
        elif status == 'unhealthy':
            return 2
        else:
            raise ValueError(f'unexpected health status: {status}')
    
    def format_status(status: str, code: int) -> str:
        match code:
            case 0:
                color = "green"
            case 1:
                color = "orange"
            case 2:
                color = "red"
            case _:
                raise ValueError(f"unexpected code: {code}")
        return f"[{color}]{status}[/{color}]"
        
    service_statuses = []
    for service, id, lifecycle_status, health_status, exit_code in matches:
        lifecycle = check_lifecycle_status(lifecycle_status, exit_code)
        health = check_health_status(health_status)
        status = max(lifecycle, health)
        table.add_row(
            service,
            id,
            format_status(lifecycle_status, lifecycle),
            format_status(health_status, health),
        )
        console.print(table)
        service_statuses.append(status)
    if len(service_statuses) == 0:
        return 2
    return max(service_statuses)
    

@cli.group()
def package():
    pass

@package.command()
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


@package.command()
def docs_serve():
    run_command('mkdocs', 'serve')

@package.command()
def docs_build():
    run_command('mkdocs', 'build', '-d', 'out/docs')

def extract_blocks(filepath: str, block: str):
    pattern = re.compile(fr"```{block} *\n(.*?)```", flags=re.MULTILINE | re.DOTALL)
    with open(filepath, 'r', encoding='utf-8') as f:
        matches = pattern.finditer(f.read())

    blocks = ''
    for match in matches:
        blocks += ''.join(match.groups())
    return blocks

@package.command()
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
        
    
@package.command()
def publish():
    run_command('poetry', 'build')
    run_command('poetry', 'publish')



# install and run 

# @click.group()
