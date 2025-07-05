from click.testing import CliRunner
from rich.prompt import Prompt


def stage_cli_prompt_responses(monkeypatch, inputs: list[str]):
    inputs = iter(inputs)
    monkeypatch.setattr(Prompt, "ask",  lambda *args, **kwargs: next(inputs))
