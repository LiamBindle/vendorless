from .parameters import parameter
from .blueprints import Blueprint
from dataclasses import dataclass


@dataclass
class Volume(Blueprint):
    name: str = parameter()

    def _template_list(self) -> list[tuple[str, str]]:
        return [
            ('volume/docker-compose.yaml', 'docker-compose.yaml')
        ]