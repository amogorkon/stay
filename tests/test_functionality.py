# only possible due to pip install -e .
from stay import Decoder, Encoder


def test_string_roundtrip():
    d = {"2": """asdf\nadsf"""}
    dumps = Encoder()
    loads = Decoder()
    assert d == list(loads(dumps(d)))[0]
