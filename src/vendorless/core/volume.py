from .parameters import parameter
from .blueprints import Blueprint
from dataclasses import dataclass


@dataclass
class Volume(Blueprint):
    """
    Represents a Docker volume configuration.
    """

    name: str = parameter()
    """The name of the Docker volume."""

    def _template_list(self) -> list[tuple[str, str]]:
        return [
            ('volume/docker-compose.yaml', 'docker-compose.yaml')
        ]