# from vendorless.core import computed_parameter, DEFERRED #service
# from vendorless.core.core import parameter
from vendorless.core import computed_parameter, parameter, ServiceTemplate, ConfigurationParameter
from typing import Any
import attr
import attrs
from dataclasses import dataclass
from rich.prompt import Prompt

import pytest


@dataclass
class C(ServiceTemplate):
    p: str = parameter()
    d: str = parameter('foo')

    @computed_parameter
    def cp(self, p):
        return f"computed-{p}"


def test_resolution():
    a = C()
    b = C()
    c = C()
    b.p = a.p
    # a.p = b.p # circular
    c.p = b.cp
    a.p = "1"
    assert b.p == "1"
    assert a.cp == "computed-1"

    a.p = "2"
    assert b.p == "2"

    # check linkage
    assert b.d == "foo"
    a.p = b.d
    assert a.p == "foo"

def test_circular():
    a = C()
    b = C()
    b.p = a.p
    a.p = b.p # circular
    with pytest.raises(RecursionError):
        _ = b.p

def test_positional_arg():
    a = C("1")
    assert a.p == "1"
    assert a.cp == "computed-1"

def test_kwarg():
    a = C(p="1")
    assert a.p == "1"
    assert a.cp == "computed-1"

def test_configuration_parameter_1():
    a = C()
    bp1 = ConfigurationParameter("param1")  # no default
    bp2 = ConfigurationParameter("param2")  # infer default

    a.p = bp1
    a.d = bp2

    assert a.d == "foo"

    bp1.value = "bar"
    assert a.p == "bar"

    bp2.value = "baz"
    assert a.d == "baz"

def test_configuration_parameter_2():
    bp1 = ConfigurationParameter("param1")  # no default
    bp2 = ConfigurationParameter("param2")  # infer default
    
    settings = {
        "param1": "hello",
        "param2": "world",
    }
    response = ConfigurationParameter.resolve(settings)
    assert settings == response


def test_configuration_parameter_3(monkeypatch):
    # Stage the input to be returned when input() is called

    bp1 = ConfigurationParameter("param1")  # no default
    bp2 = ConfigurationParameter("param2")  # infer default

    inputs = iter(["hello", "world"])
    monkeypatch.setattr(Prompt, "ask",  lambda *args, **kwargs: next(inputs))
    
    settings = {
        "param1": "hello",
        "param2": "world",
    }
    response = ConfigurationParameter.resolve({})
    assert settings == response