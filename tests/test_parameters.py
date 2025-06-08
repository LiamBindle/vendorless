from vendorless.param import parameter, computed_parameter, service

def test_params():

    @service
    class C:
        p: str

        @computed_parameter
        def cp(self, p):
            return f"computed-{p}"
    
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