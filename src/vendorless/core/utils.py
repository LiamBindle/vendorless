from importlib.abc import Traversable
import importlib.resources
from pathlib import PurePosixPath
from typing import Iterator

def get_template_dir(obj: object) -> Traversable:
    vl_module = obj.__class__.__module__
    assert vl_module.startswith('vendorless.')
    assert len(vl_module.split('.')) >= 2
    return importlib.resources.files(f'{".".join(vl_module.split(".")[:2])}.templates')


def get_template_dir_files(template_dir: Traversable, relative_to: PurePosixPath = PurePosixPath("")) -> Iterator[tuple[PurePosixPath, Traversable]]:
    for child in template_dir.iterdir():
        rel_path = relative_to / child.name
        if child.is_dir():
            yield from get_template_dir_files(child, rel_path)
        else:
            yield child, rel_path