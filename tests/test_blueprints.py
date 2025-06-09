from vendorless.core import computed_parameter, Parameter, Blueprint

from dataclasses import dataclass

import pytest

def test_enforce_is_dataclass():

    @dataclass
    class X(Blueprint):
        pass
    x = X()

    with pytest.raises(TypeError):
        class X(Blueprint):
            pass
        x = X()


def test_template_files():
    from vendorless.core.blueprints import _DummyBlueprint

    x = _DummyBlueprint()

    yielded_templates = set()

    for path, relative_path in x._template_files():
        if relative_path is not None:
            relative_path = str(relative_path)
        yielded_templates.add((path.name, relative_path))

    assert ('docker-compose.yaml', None) in yielded_templates
    assert ('cookiecutter.json', 'module/cookiecutter.json') in yielded_templates
    