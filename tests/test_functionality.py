
import os, sys
here = os.path.split(os.path.abspath(os.path.dirname(__file__)))
src = os.path.join(here[0], "src/stay")
sys.path.insert(0,src)
print(sys.path)

from stay import dumps, loads, load
from pydantic.dataclasses import dataclass
from typing import List
from dataclasses import asdict

d = {"2": """asdf\nadsf"""}
assert d == list(loads(dumps(d)))[0]

@dataclass
class Foo:
    num: int
    foo: str
    bar: str
    baz: List[int]

D1 = {"num":1, "foo": "qwer", "bar": "asdf\nadsf", "baz": [1,2,3]}

with open("test", "w") as f:
    f.write(dumps(D1))
    
with open("test") as f:
    for x in load(f):
        D2 = asdict(Foo(**x))

assert D1 == D2

def test_string_roundtrip():
    d = [{"a": '3', "b":'45'}]
    s = dumps(d)
    D = list(loads(s))
    assert d == D
