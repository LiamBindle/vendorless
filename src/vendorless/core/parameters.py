
from dataclasses import dataclass

import inspect
from typing import Any


@dataclass
class ParameterReference:
    obj: object
    param: Any

    def dereference(self):
        return self.param.__get__(self.obj, self.obj.__class__)

UNRESOLVED = object()

class Parameter:
    def __init__(self, default=UNRESOLVED) -> None:
        self.default = default

    def __set_name__(self, owner, name):
        self.attr_name = f'_{name}'

    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        is_resolved = hasattr(instance, self.attr_name) and not isinstance(instance, ParameterReference)

        if not is_resolved:
            return ParameterReference(instance, self)
        
        value = getattr(instance, self.attr_name)
        if isinstance(value, ParameterReference):
            value = value.dereference()

        return value
    
    def __set__(self, instance, value):
        if value is self:
            value = self.default
        
        if value is not UNRESOLVED:
            setattr(instance, self.attr_name, value)
    
    def __repr__(self) -> str:
        return f"<parameter {self.attr_name}>"
    
def parameter(default=UNRESOLVED) -> Any:
    return Parameter(default)

class computed_parameter: # pylint: disable=invalid-name
    def __init__(self, func):
        self.func = func
        self.attr_name = f"_{func.__name__}"

        sig = inspect.signature(func)

        self.precursors = [
            name for name, param in sig.parameters.items()
            if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ]
        assert self.precursors[0] == 'self'
        self.precursors = self.precursors[1:]
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        args = list(getattr(instance, p) for p in self.precursors)
        if any(isinstance(a, ParameterReference) for a in args):
            return ParameterReference(instance, self)
        value = self.func(instance, *args)
        return value
