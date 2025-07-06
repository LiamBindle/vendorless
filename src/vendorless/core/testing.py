from pathlib import Path
from click.testing import CliRunner, Result
from rich.prompt import Prompt
from vendorless.core.cli import main
import os
import yaml
import time

import subprocess
from typing import Callable, Generator, Iterator

from contextlib import contextmanager

import pytest


def stage_cli_prompt_responses(monkeypatch, inputs: list[str]):
    inputs_iterator: Iterator[str] = iter(inputs)
    monkeypatch.setattr(Prompt, "ask",  lambda *args, **kwargs: next(inputs_iterator))

@contextmanager
def temp_cli() -> Generator[Callable[[list[str]], Result], None, None]:
    runner = CliRunner()
    with runner.isolated_filesystem():
        def run_args(args: list[str]) -> Result:
            return runner.invoke(main, args)
        yield run_args


class Tester:
    def __init__(self, monkeypatch, temp_dir: Path) -> None:
        self.monkeypatch = monkeypatch
        self.temp_dir = temp_dir
        self.runner = CliRunner()

    
    def stage_prompt_responses(self, inputs: list[str]):
        inputs_iterator: Iterator[str] = iter(inputs)
        self.monkeypatch.setattr(Prompt, "ask",  lambda *args, **kwargs: next(inputs_iterator))
    
    def run_cli(self, args: list[str], expect_failure:bool = False, return_exit_code: bool = False):
        result = self.runner.invoke(main, args)

        if return_exit_code:
            return result.exit_code
        
        if not expect_failure:
            assert result.exit_code == 0, f"stderr: {result.stderr if hasattr(result, 'stderr') else 'N/A'}"
        else:
            assert result.exit_code != 0, "CLI did not fail when an error was expected"
    
    def run_command(self, cmd: list[str], expect_failure:bool = False, return_exit_code: bool = False):
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        if return_exit_code:
            return result.returncode
        
        if not expect_failure:
            assert result.returncode == 0, f"stderr: {result.stderr if hasattr(result, 'stderr') else 'N/A'}"
        else:
            assert result.returncode != 0, "CLI did not fail when an error was expected"
    
    def write_yaml(self, data: dict, file_path: str):
        with open(file_path ,'w') as f:
            yaml.safe_dump(data, f)
    
    @contextmanager
    def run_stack(self, blueprint: str, config: dict):
        self.write_yaml(config, 'config.yaml')
        self.run_cli([
            'core',
            'render',
            blueprint,
            '--config', 'config.yaml',
            '--output', 'test_stack'
        ])
        self.run_cli([
            'core',
            'start',
            'test_stack',
        ])
        
        while status := self.run_cli(['core', 'status', 'test_stack'], return_exit_code=True):
            if status != 0:
                break
            time.sleep(0.1)
        
        assert status == 0, "The test stack failed to start properly"
        yield
        self.run_cli([
            'core',
            'stop',
            'test_stack',
            '--destroy'
        ])

    
    # start docker
    # wait for healthy (with timeout)
    # run tests...
    # clean up all docker resources



@pytest.fixture
def tester(monkeypatch, tmp_path: Path) -> Generator[Tester, None, None]:
    # setup
    initial_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield Tester(monkeypatch, tmp_path)
    
    # cleanup
    os.chdir(initial_cwd)

