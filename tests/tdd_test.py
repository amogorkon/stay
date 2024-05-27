"""Here live all the tests that are expected to fail because their functionality is not implemented yet.
Test-Driven Development is done in the following order:
    1. Create a test that fails.
    2. Write the code that makes the test pass.
    3. Check how long the test took to run.
    4. If it took longer than 1 second, move it to integration tests. Otherwise, move it to unit tests.
"""

import directives as drv
import pytest
from stay import Decoder, ParsingError, dumps, loads

xfail = pytest.mark.xfail(strict=True)


@xfail
def test_empty_list_of_lists():
    s = """
list of lists:::[
[[] [[]]]
[]
]
"""
    assert list(loads(s)) == [{"list of lists": [[[], [[]]], []]}]


@xfail
def test_nothing():  # sourcery skip: simplify-empty-collection-comparison
    assert list(loads(None)) == []
    assert list(loads([])) == []
    assert list(loads("")) == []
    with open("nothing") as f:
        assert list(loads(f)) == []


@xfail
def test_include():
    loads = Decoder(commands={"include": drv.include})
    s = """
% include include-test %
"""
    with pytest.raises(ParsingError) as exc:
        list(loads(s))
    assert "%" in str(exc.value)

    s = """
% include include-test
"""
    assert list(loads(s)) == [{"a": "23", "b": {"c": "34", "d": "30"}}]

    loads = Decoder()
    s = """
% include include-test
"""
    with pytest.raises(ParsingError) as exc:
        list(loads(s))
    assert "command include not defined" in str(exc.value)


@xfail
def test_list_of_lists():
    s = """
list of lists:::[
    :::[
    a
    b
        ] inner
    c
] list of lists
"""
    assert list(loads(s)) == [{"list of lists": (("a", "b"), "c")}]


@xfail
def test_complex_list():
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
    assert list(loads(s)) == [{"list of lists": (("a", "b", "c"), ("1", "2", "3"), ("foo", "bar"))}]


@xfail
def test_dump_multi_docs():
    it = [{1: 2}, {2: 3}]
    assert (
        dumps(it)
        == """1: 2
===
2: 3
"""
    )


@xfail
def test_list_to_set_struct():
    decode = Decoder(struct_directives={"list_to_set": drv.list_to_set})

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


@xfail
def test_context():
    decode = Decoder(key_directives={"context": drv.context})

    s = """
<context
nc: http://release.niem.gov/niem/niem-core/4.0/#
age: nc:PersonAgeMeasure
name: nc:PersonName
given: nc:PersonGivenName
surname: PersonSurName
nickname: PersonPreferredName
>
age: 14
given: Mortimer
surname: Smith
nickname: Morty
"""
    assert list(decode(s)) == [
        {
            "http://release.niem.gov/niem/niem-core/4.0/#PersonAgeMeasure": "14",
            "http://release.niem.gov/niem/niem-core/4.0/#PersonGivenName": "Mortimer",
            "PersonSurName": "Smith",
            "PersonPreferredName": "Morty",
        }
    ]


@xfail
def test_short_list_to_set_struct():
    decode = Decoder(struct_directives={"list_to_set": drv.list_to_set})

    s = """
<list_to_set>
set: [1 2 2 3]
"""
    assert list(decode(s)) == [{"set": set(["1", "2", "3"])}]
