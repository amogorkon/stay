from stay import Decoder, dumps, loads


def test_anything():
    assert list(loads("\n")) == [{}]
    assert list(loads("\n\n\n")) == [{}]

    s = """
===
===
"""
    assert list(loads(s)) == [{}, {}, {}]


def test_simple_dump():
    d1 = {"a": "c"}
    s = dumps(d1)
    assert s == "a: c\n"


def test_dict():
    s = "a: b\n"
    assert list(loads(s)) == [{"a": "b"}]

    s = """
x: y
y: z
"""
    assert list(loads(s)) == [{"x": "y", "y": "z"}]


def test_comment():
    s = "# adsf\n"
    assert list(loads(s)) == [{}]

    s = """
###
asdf
###

a: b
# bdesf
"""
    assert list(loads(s)) == [{"a": "b"}]

    s = """
### asdf ###
a: b
"""
    assert list(loads(s)) == [{"a": "b"}]


def test_line_comments():
    comments = lambda *args: lambda line: line.split("#")[0]
    decode = Decoder(line_directives={"comments": commenting})
    s = """
a: 28 # adsf
"""
    assert list(decode(s)) == [{"a": "28 # adsf"}]

    s = """
<comments>
a: 28 # adsf
</comments>
b: 29 # ouewr
<comments>
c: 30 # fdad
"""
    assert list(decode(s)) == [
        {
            "a": "28",
            "b": "29 # ouewr",
            "c": "30",
        }
    ]


def test_key_comments():
    comments = lambda *args: lambda s: s.split("#")[0]
    decode = Decoder(key_directives={"comments": comments})

    s = """
<comments>
strange # explanation : value
"""
    assert list(decode(s)) == [{"strange": "value"}]


def test_key_value_comments():
    comments = lambda *args: lambda s: s.split("#")[0]
    decode = Decoder(key_directives={"comments": comments}, value_directives={"comments": comments})

    s = """
<comments>
strange # explanation : value # explanation
"""
    assert list(decode(s)) == [{"strange": "value"}]


def test_long():
    text = """
foo:::
1
2
3


:::
"""
    assert list(loads(text)) == [{"foo": "1\n2\n3\n\n"}]


def test_complex():
    text = """
name:
    family: adsf
    call:
        foo:::
1
2
:::
"""
    assert list(loads(text)) == [{"name": {"family": "adsf", "call": {"foo": "1\n2"}}}]


def test_list():
    text = """
matrix:::[

[1 2 3]
[4 5 6]
[7 8 9]
foo bar
]:::
"""
    assert list(loads(text)) == [{"matrix": (("1", "2", "3"), ("4", "5", "6"), ("7", "8", "9"), "foo bar")}]

    text = """
list of lists: [1 2 [3 4] []]
"""
    # assert list(decode(text)) == [{"list of lists": ["1", "2", ["3", "4"], []]}]


def test_simple_list():
    s = """
lists:::[
1
2
3
]
"""
    assert list(loads(s)) == [{"lists": ("1", "2", "3")}]


def test_anonymous_list():
    s = """
:::[
a: 1
a: 2
a: 2
b: 3
]:::
"""
    assert list(loads(s)) == [{"": ("a: 1", "a: 2", "a: 2", "b: 3")}]
