from vendorless.core.service import Service

def test_service_def_1():
    a = Service()
    assert a.name is None
    assert a.age is None