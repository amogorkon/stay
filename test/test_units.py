
# importing the sibling folder is not as easy as it should be..
import os, sys
here = os.path.split(os.path.abspath(os.path.dirname(__file__)))
src = os.path.join(here[0], "src/stay")
sys.path.insert(0,src)

from stay import Encoder, Decoder, __version__, ParsingError
import directives as drv

from pytest import fixture
import pytest

skip = pytest.mark.skip("test still WIP")


@fixture
def decode():
    return Decoder()

@fixture
def encode():
    return Encoder()

def test_nothing(decode):
    assert list(decode(None)) == []
    assert list(decode([])) == []
    assert list(decode("")) == []
    with open("nothing") as f:
        assert list(decode(f)) == []

def test_anything(decode):
    assert  list(decode("\n")) == [{}]
    assert list(decode("\n\n\n")) == [{}]
    
    s = """
===
===
"""
    assert list(decode(s)) == [{}, {}, {}]

def test_dict(decode):
    s = "a: b\n"
    assert list(decode(s)) == [{"a": "b"}]

    s = """
x: y
y: z
"""
    assert list(decode(s)) == [{'x': 'y', 'y': 'z'}]


def test_simple_dump(encode):
    d1 = {"a": "c"}
    s = encode(d1)
    assert s == "a: c\n"

def test_comment(decode):
    s = "# adsf\n"
    assert list(decode(s)) == [{}]

    s = """
###
asdf
###

a: b
# bdesf
"""
    assert list(decode(s)) == [{'a': 'b'}]
    
    s = """
### asdf ###
a: b
"""
    assert list(decode(s)) == [{'a': 'b'}]


def test_line_comments():
    comments = lambda line: line.split("#")[0]
    decode = Decoder(line_directives={"comments": comments})
    s = """
a: 28 # adsf
"""
    assert list(decode(s)) == [{'a': '28 # adsf'}]

    s = """
<comments>
a: 28 # adsf
</comments>
b: 29 # ouewr
<comments>
c: 30 # fdad
"""
    assert list(decode(s)) == [{'a': '28',
                                'b': "29 # ouewr",
                                "c": "30",
                            }]

def test_key_comments():
    comments = lambda s: s.split("#")[0]
    decode = Decoder(key_directives={"comments": comments})
    
    s = """
<comments>
strange # explanation : value
"""
    assert list(decode(s)) == [{"strange": "value"}]

def test_key_value_comments():
    comments = lambda s: s.split("#")[0]
    decode = Decoder(key_directives={"comments": comments},
                    value_directives={"comments": comments})

    s = """
<comments>
strange # explanation : value # explanation
"""
    assert list(decode(s)) == [{"strange": "value"}]

def test_include():
    decode = Decoder(commands={"include": drv.include})
    s = """
% include include-test %
"""
    with pytest.raises(ParsingError) as exc:
        list(decode(s))
    assert "%" in str(exc.value)

    s = """
% include include-test
"""
    assert list(decode(s)) == [{'a': '23',
                                'b': {'c': '34',
                                    'd': '30'}
                                }]

    decode = Decoder()
    s = """
% include include-test
"""
    with pytest.raises(ParsingError) as exc:
        list(decode(s))
    assert "command include not defined" in str(exc.value)


def test_long(decode):
    text = """
foo:::
1
2
3


:::   
"""
    assert list(decode(text)) == [{'foo': '1\n2\n3\n\n'}]

def test_complex(decode):
    text = """
name: 
    family: adsf
    call: 
        foo:::
1
2
:::
"""
    assert list(decode(text)) == [{'name': {"family": "adsf", "call": 
                                           {"foo": "1\n2"}}}]

def test_list(decode):
    text = """
matrix:::[

[1 2 3]
[4 5 6]
[7 8 9]
foo bar
]:::
"""
    assert list(decode(text)) == [{"matrix": (('1','2','3'), 
                                             ('4','5','6'), 
                                             ('7','8','9'), 
                                             "foo bar")}]


@skip
def test_empty_list_of_lists(decode):
    s = """
list of lists:::[
:::[
:::[
]
]
]
"""
    assert list(decode(s)) == [{"list of lists": (((),),)}]

def test_simple_list(decode):
    s = """
lists:::[
1
2
3
]
"""
    assert list(decode(s)) == [{"lists": ("1", "2", "3")}]

@skip
def test_list_of_lists(decode):
    s = """
list of lists:::[
    :::[
    a
    b
        ] inner
    c
] list of lists
"""
    assert list(decode(s)) == [{"list of lists": (("a", "b"), "c")}]

@skip
def test_complex_list(decode):
    s = """
list of lists:::[
[a b c]
inner:::[
1
2
3
] inner
:::[
foo
bar
]
"""
    assert list(decode(s)) == [{"list of lists": (("a", "b", "c"), ("1", "2", "3"), ("foo", "bar"))}]

def test_dump_multi_docs(encode):
    it = [{1:2},{2:3}]
    assert encode(it) == """1: 2
===
2: 3
"""

@skip
def test_anonymous_list(decode):
    
    s = """
:::[
a: 1
a: 2
a: 2
b: 3
]:::
"""
    assert list(decode(s)) == [{'': ("a: 1", "a: 2", "a: 2", "b: 3")}]


def test_short_list_to_set_struct():
    list_to_set = lambda token, struct: set(struct)
    decode = Decoder(struct_directives={"list_to_set": list_to_set})

    s = """
<list_to_set>
set: [1 2 2 3]
"""
    assert list(decode(s)) == [{"set": set(["1", "2", "3"])}]

def test_list_to_set_struct():
    list_to_set = lambda token, struct: set(struct)
    decode = Decoder(struct_directives={"list_to_set": list_to_set})

    s = """
<list_to_set>
set:::[
1
2
2
3
]
"""
    assert list(decode(s)) == [{"set": set(["1", "2", "3"])}]