from click.testing import CliRunner, Result
from rich.prompt import Prompt
from vendorless.core.cli import main

from typing import Callable, Generator, Iterator

from contextlib import contextmanager


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