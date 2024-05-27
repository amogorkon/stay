# only possible due to pip install -e .
from stay import dumps, loads


def test_string_roundtrip():
    d = {"2": """asdf\nadsf"""}
    assert d == list(loads(dumps(d)))[0]
