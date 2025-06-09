from ctypes import ArgumentError
import inspect

from dataclasses import dataclass


class parameter_base:  # pylint: disable=invalid-name
    pass


@dataclass
class reference:
    obj: object
    param: parameter_base

    def dereference(self):
        return self.param.__get__(self.obj, self.obj.__class__)


class parameter(parameter_base):  # pylint: disable=invalid-name
    def __init__(self, name):
        self.attr_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        is_resolved = hasattr(instance, self.attr_name) and not isinstance(instance, reference)

        if not is_resolved:
            return reference(instance, self)
        
        value = getattr(instance, self.attr_name)
        if isinstance(value, reference):
            value = value.dereference()
            
            ## TO SAVE
            # if not isinstance(value, reference):
            #     self.__set__(instance, value)

        return value
    
    def __set__(self, instance, value):
        return setattr(instance, self.attr_name, value)
    
    def __repr__(self) -> str:
        return f"<parameter {self.attr_name}>"

class computed_parameter(parameter_base): # pylint: disable=invalid-name
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
        if any(isinstance(a, reference) for a in args):
            return reference(instance, self)
        value = self.func(instance, *args)
        return value
    
        ## TO SAVE
        # if not hasattr(instance, self.attr_name):
        #     args = list(getattr(instance, p) for p in self.precursors)
        #     if any(isinstance(a, reference) for a in args):
        #         return reference(instance, self)
        #     value = self.func(instance, *args)
        #     setattr(instance, self.attr_name, value)
        # return getattr(instance, self.attr_name)

class _DEFERRED:
    def __repr__(self) -> str:
        return 'DEFERRED' 
    
from typing import Any
DEFERRED: Any = _DEFERRED()

objects: dict[str, list] = {}

def stack_object(type: str):

    def parameterized(cls):

        # Collect annotated fields and their defaults (if any)
        parameters = []

        for name, type_hint in cls.__annotations__.items():
            default = getattr(cls, name, DEFERRED)
            parameters.append(
                inspect.Parameter(
                    name,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    default=default,
                    annotation=type_hint,
                )
            )

            setattr(cls, name, parameter(name))

        sig = inspect.Signature(parameters)

        # Generate the __init__ method
        def __init__(self, **kwargs):
            bound = sig.bind(**kwargs)
            bound.apply_defaults()

            for name, value in bound.arguments.items():
                if value is not DEFERRED:
                    setattr(self, name, value)
                    
            if type not in objects:
                objects[type] = []
            objects[type].append(self)
        
        __init__.__signature__ = inspect.Signature([inspect.Parameter('self', inspect.Parameter.POSITIONAL_OR_KEYWORD)] + parameters)
        cls.__init__ = __init__
        return cls
    return parameterized

service = stack_object('service')
volume = stack_object('volume')
network = stack_object('network')
import attr

@service
@attr.s(auto_attribs=True)
class foo:
    a: str
    b: str = 1

    @computed_parameter
    def c(self, a, b):
        return f"{a}-{b}"

# x = foo()
# print("here")