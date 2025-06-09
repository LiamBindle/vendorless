from _typeshed import Incomplete
from ctypes import ArgumentError as ArgumentError
from dataclasses import dataclass

class parameter_base: ...

@dataclass
class reference:
    obj: object
    param: parameter_base
    def dereference(self): ...

class parameter(parameter_base):
    attr_name: Incomplete
    def __init__(self, name) -> None: ...
    def __get__(self, instance, owner): ...
    def __set__(self, instance, value): ...

class computed_parameter(parameter_base):
    func: Incomplete
    attr_name: Incomplete
    precursors: Incomplete
    def __init__(self, func) -> None: ...
    def get_func_args(self, instance): ...
    def __get__(self, instance, owner): ...

objects: dict[str, list]
DEFERRED: Incomplete

def stack_object(type: str): ...

service: Incomplete
volume: Incomplete
network: Incomplete

class foo:
    def __init__(self, a=DEFERRED, b=DEFERRED) -> None: ...
    a: str
    b: str
    @computed_parameter
    def c(self, a, b): ...
