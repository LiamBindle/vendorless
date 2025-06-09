import importlib.resources as resources
from jinja2 import Environment, BaseLoader, TemplateNotFound
import importlib.resources

class ResourceLoader(BaseLoader):
    def __init__(self, obj):
        vl_module = obj.__class__.__module__
        assert vl_module.startswith('vendorless.')
        assert len(vl_module.split('.')) >= 2
        self.files = importlib.resources.files(f'{".".join(vl_module.split(".")[:2])}.templates')

    def get_source(self, environment, template):
        # resource_path = f"{self.folder}/{template}"
        try:
            contents = (self.files / template).read_text()
        except FileNotFoundError:
            raise TemplateNotFound(template)

        return contents, str(template), lambda: True