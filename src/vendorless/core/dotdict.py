from typing import Callable
import yaml




class DotDict(dict):
    def __init__(self, **kwargs):
        super().__init__()
        annotations = getattr(self.__class__, '__annotations__', {})
        # Initialize all annotated attributes to None or default
        for key in annotations:
            self[key] = kwargs.get(key, None)
        # Set any additional kwargs (allow override)
        for key, value in kwargs.items():
            self[key] = value

    def __getattr__(self, key): # -> Reference:
        # return a reference if it's a dotdict or unresolved

        if key in self:
            return self[key]
        # For extensibility: don't raise AttributeError
        self[key] = DotDict()
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]

    def to_dict(self):
        def convert(value):
            if isinstance(value, DotDict):
                return {k: convert(v) for k, v in value.items()}
            return value
        return convert(self)

# class Reference:
#     def __init__(self, obj: object, attr: str) -> None:
#         pass

# class Unresolved:
#     def __init__(self, precursors: list[References], obj: DotDict, attr: str, callback: Callable):
#         pass


# Optional: make YAML dump use to_dict
def dotdict_representer(dumper, data):
    return dumper.represent_dict(data.to_dict())

yaml.add_representer(DotDict, dotdict_representer)

if __name__ == '__main__':
    x = DotDict()