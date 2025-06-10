from vendorless.core import Blueprint

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
    yielded_templates = set(src_dest_pair for src_dest_pair in x._template_list())
    assert ('volume/docker-compose.yaml', 'volume/docker-compose.yaml') in yielded_templates
    assert ('package/cookiecutter.json', 'package/cookiecutter.json') in yielded_templates


# def test_render_postgres():
#     from vendorless.core import Volume
#     from vendorless.postgres import PostgresDatabase
#     from pathlib import Path

#     v = Volume()
#     pg = PostgresDatabase(
#         volume_name=v.name,
#         data_path="/pgdata"
#     )
#     v.name = "pgdata_volume"

#     root = Path('.build/')
#     Blueprint.render_stack(root)