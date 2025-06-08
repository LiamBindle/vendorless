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


def service(cls):
    # inspect all attributes
    #   - attributes become parameters

    annotations = cls.__annotations__

    for name in annotations:
        setattr(cls, name, parameter(name))

    # Generate the __init__ method
    def __init__(self, **kwargs):
        unexpected_args = set(kwargs.keys()) - set(annotations)
        if unexpected_args:
            raise ArgumentError(f"Unexpected argument: {", ".join(unexpected_args)}")

        for name in annotations:
            if name in kwargs:
                setattr(self, name, kwargs[name])


    cls.__init__ = __init__
    return cls

if __name__ == '__main__':
    @service
    class foo:
        a: str
        b: str

        @computed_parameter
        def c(self, a, b):
            return f"{a}-{b}"
        
    x = foo(a=1, b=2)
    y = foo()
    print(x.c)