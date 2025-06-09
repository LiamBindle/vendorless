
import weakref
from dataclasses import dataclass, is_dataclass

_blueprints: weakref.WeakValueDictionary[int, 'Blueprint'] = weakref.WeakValueDictionary()

from typing import Generator, Iterator
from importlib.resources.abc import Traversable
from pathlib import PurePosixPath
import importlib.resources

def get_template_dir_files(template_dir: Traversable, relative_to: PurePosixPath = PurePosixPath("")) -> Generator[tuple[Traversable, PurePosixPath | None], None, None]:
    for child in template_dir.iterdir():
        rel_path = relative_to / child.name
        if child.is_dir():
            yield from get_template_dir_files(child, rel_path)
        else:
            if child.name == 'docker-compose.yaml':
                rel_path = None
            yield child, rel_path


class Blueprint:
    def __init__(self) -> None:
        self._assert_is_dataclass()
    
    def _assert_is_dataclass(self):
        if not is_dataclass(self):
            raise TypeError(f"{self.__class__} must be a dataclass")

    def __post_init__(self):
        self._assert_is_dataclass()
        _blueprints[id(self)] = self
    
    def _template_files(self):
        vl_module = self.__class__.__module__
        assert vl_module.startswith('vendorless.')
        assert len(vl_module.split('.')) >= 2

        template_dir = importlib.resources.files(f'{".".join(vl_module.split(".")[:2])}.templates')
        yield from get_template_dir_files(template_dir)

    @classmethod
    def all_registered(cls=None) -> list['Blueprint']:
        blueprints: list['Blueprint'] = [b for b in _blueprints.values()]
        if cls is not None:
            blueprints = [b for b in blueprints if isinstance(b, cls)]
        return blueprints

@dataclass
class _DummyBlueprint(Blueprint):
    pass