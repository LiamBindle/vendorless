

import yaml
import weakref
from dataclasses import dataclass, is_dataclass, asdict

_service_templates: weakref.WeakValueDictionary[int, 'ServiceTemplate'] = weakref.WeakValueDictionary()

from typing import Generator, Iterator
from importlib.resources.abc import Traversable
from pathlib import PurePosixPath, Path
import importlib.resources

import jinja2

def get_template_dir_files(template_dir: Traversable, relative_to: PurePosixPath = PurePosixPath("")) -> Generator[str, None, None]:
    for child in template_dir.iterdir():
        rel_path = relative_to / child.name
        if child.is_dir():
            yield from get_template_dir_files(child, rel_path)
        else:
            yield str(rel_path)

from .templating import ResourceLoader

class ServiceTemplate:
    def __init__(self) -> None:
        self._assert_is_dataclass()
    
    def _assert_is_dataclass(self):
        if not is_dataclass(self):
            raise TypeError(f"{self.__class__} must be a dataclass")

    def __post_init__(self):
        self._assert_is_dataclass()
        _service_templates[id(self)] = self

    def _copy_list(self) -> list[tuple[str, str]]:
        return []
    
    def _template_list(self) -> list[tuple[str, str]]:
        vl_module = self.__class__.__module__
        assert vl_module.startswith('vendorless.')
        assert len(vl_module.split('.')) >= 2

        template_dir = importlib.resources.files(f'{".".join(vl_module.split(".")[:2])}.templates')
        files = []
        for template_file in get_template_dir_files(template_dir):
            files.append((template_file, template_file))
        return files
    
    def _render(self, stack_root: Path, docker_compose: dict):
        loader = ResourceLoader(self)
        env = jinja2.Environment(
            loader=loader
        )
        context = asdict(self)

        dsts = {}
        copies = set()
        for src, dst in self._template_list():
            if dst in dsts:
                raise ValueError(f"multiple input files render '{dst}'")
            dsts[dst] = src
        
        for src, dst in self._copy_list():
            if dst in dsts:
                raise ValueError(f"multiple input files render '{dst}'")
            dsts[dst] = src
            copies.add(dst)

        for dst, src in dsts.items():
            dst = stack_root / env.from_string(dst).render(context)
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst in copies:
                with open(dst, 'wb') as f:
                    f.write((loader.files / src).read_bytes())  # TODO: test
            else:
                template = env.get_template(src)
                rendered = template.render(context)
                if dst.name == 'docker-compose.yaml':
                    
                    dc_data: dict = yaml.safe_load(rendered)
                    kv: dict
                    for first_key, kv in dc_data.items():
                        if first_key not in docker_compose:
                            docker_compose[first_key] = {}
                        
                        for second_key, v in kv.items():
                            if second_key in docker_compose[first_key]:
                                raise ValueError(f'multiple service templates render {first_key}.{second_key} ')
                            docker_compose[first_key][second_key] = v
                else:
                    with open(dst, 'w') as f:
                        f.write(rendered)


    @classmethod
    def render_stack(cls, stack_root: str | Path):
        if isinstance(stack_root, str):
            stack_root = Path(stack_root)
        docker_compose = {}
        for service_template in _service_templates.values():
            service_template._render(stack_root, docker_compose)
        with open(stack_root/'docker-compose.yaml', 'w') as f:
            yaml.safe_dump(docker_compose, f)

@dataclass
class _DummyServiceTemplates(ServiceTemplate):
    pass