from .parameters import parameter
from .service_template import ServiceTemplate
from dataclasses import dataclass


@dataclass
class Volume(ServiceTemplate):
    """
    Represents a Docker volume configuration.
    """

    name: str = parameter()
    """The name of the Docker volume."""

    def _template_list(self) -> list[tuple[str, str]]:
        return [
            ('volume/docker-compose.yaml', 'docker-compose.yaml')
        ]