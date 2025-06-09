from vendorless.core import computed_parameter, service, DEFERRED
import attr

import pytest


@service
@attr.s(auto_attribs=True)
class C:
    p: str = DEFERRED

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