
from dataclasses import dataclass
import warnings

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
        
        if isinstance(value, BlueprintParameter):
            value.register_dependant(ParameterReference(instance, self))
        elif value is not UNRESOLVED:
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

INFER=object()


class BlueprintParameter:
    _ALL_BLUEPRINT_PARAMETERS: list['BlueprintParameter'] = []

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        self._value = value
        for ref in self._dependants:
            ref.param.__set__(ref.obj, value)

    def __init__(self, name: str, description: str='', default=INFER) -> None:
        self.name = name
        self.default = default
        self.description = description
        BlueprintParameter._ALL_BLUEPRINT_PARAMETERS.append(self)
        self._dependants: list[ParameterReference] = []
        self.value = UNRESOLVED if default is INFER else default

    
    def register_dependant(self, reference: ParameterReference):
        if self.default is INFER and reference.param.default is not UNRESOLVED:
            if self.value != UNRESOLVED and self.value != reference.param.default:
                warnings.warn(
                    f"Blueprint parameter '{self.name}' is inferring a default value from parameters with different values."
                    f"Previous default value: {self.value}. New default value: {reference.param.default}."
                )
            self.value = reference.param.default
        self._dependants.append(reference)
        reference.param.__set__(reference.obj, self.value)