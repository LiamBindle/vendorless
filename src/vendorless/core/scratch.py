
from dataclasses import dataclass, field
import attrs

from typing import Generic, TypeVar

# from vendorless.core.core import parameter, DEFERRED, parameter_base, reference


class parameter_base:  # pylint: disable=invalid-name
    pass


@dataclass
class AttributeReference:
    obj: object
    param: parameter_base

    def dereference(self):
        return self.param.__get__(self.obj, self.obj.__class__)

T = TypeVar('T')

class Deferred(Generic[T], parameter_base):
    def __set_name__(self, owner, name):
        self.attr_name = f'_{name}'

    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        is_resolved = hasattr(instance, self.attr_name) and not isinstance(instance, AttributeReference)

        if not is_resolved:
            return AttributeReference(instance, self)
        
        value = getattr(instance, self.attr_name)
        if isinstance(value, AttributeReference):
            value = value.dereference()

        return value
    
    def __set__(self, instance, value):
        if value is not self:
            setattr(instance, self.attr_name, value)
    
    def __repr__(self) -> str:
        return f"<parameter {self.attr_name}>"

import inspect
class computed_attribute(parameter_base): # pylint: disable=invalid-name
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
    
    def get_func_args(self, instance):
        return list(getattr(instance, p) for p in self.precursors)
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        # TO COMPUTE DYNAMICALLY
        args = list(getattr(instance, p) for p in self.precursors)
        if any(isinstance(a, AttributeReference) for a in args):
            return AttributeReference(instance, self)
        value = self.func(instance, *args)
        return value


@dataclass
class Blueprint:
    def _template_