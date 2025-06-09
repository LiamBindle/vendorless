from vendorless.core.dotdict import DotDict
import yaml

def sample_dotdict():
    d = DotDict()
    d.a = 'a'
    d.b = 'b'
    d.c.x = 1
    d.c.y = 2
    d.c.z = 3
    return d
    

def test_dotdict_nested():
    d = sample_dotdict()
    assert d == {
        'a': 'a',
        'b': 'b',
        'c': {
            'x': 1,
            'y': 2,
            'z': 3,
        },
    }

def test_dotdict_to_yaml():
    d = sample_dotdict()
    yaml_str = yaml.dump(d)
    d_parsed = yaml.safe_load(yaml_str)
    assert d == d_parsed