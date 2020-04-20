
from shlex import split
from enum import Enum
from collections.abc import Iterable
from collections import deque
from functools import partial
from typing import Union, Dict, List, Sequence, Iterator
from dataclasses import asdict, dataclass, is_dataclass
import logging
from io import TextIOBase


logger = logging.getLogger()


T = Enum("Token", "start simple key comment long list dict graph directive")
D = Enum("Directives", "line key value struct meta")

__version__ = 464

Result = Enum("Result", "drv line")

class ParsingError(Exception):
    pass

class State:
    def __init__(self, context):
        self.tokens = deque([T.start])

        # the dictionary to be yielded as one document
        self.doc = {}

        # dicts of dicts can contain any other datastructure, thus 
        self.dict_stack = deque()
        # for lists - maybe unifieable?
        self.stack = []
        self.value = []  # Current value in the doc
        self.key = None  # Current key in the doc

        self.context = {}  # can be used by directives to manipulate and change content ad hoc
        # all directives to be executed at certain points, in the order as activated
        self.directives = {D.line: {},
                            D.key: {},
                            D.value: {},
                            D.struct: {},
                            D.meta: {}}

def level(line, spaces_per_indent):
    line = line.expandtabs(tabsize=spaces_per_indent)
    return (len(line) - len(line.lstrip()))//spaces_per_indent

def _do_start(n, line, st):
    return None, None

def _do_comment(n, line, st):
    return ..., None

def _do_long(n, line, st):
    if line.startswith(":::"):
        return st.tokens.pop(), "\n".join(st.value)
    else:
        st.value.append(line)
        return ..., None

def _do_list(n, line, st):
    line = line.strip()

    if line.startswith("]"):
        token = st.tokens.pop()
        if st.tokens[-1] is not T.list:
            return token, tuple(st.stack)
        else:
            p = st.stack.pop()
            st.stack[0] =  tuple(p)
            return ..., None
    
    if line.startswith(r"\]"):
        line = line[1:]
    
    if line == "":
        return ..., None

    # like a matrix, for instance
    if line.startswith("[") and line.endswith("]"):
        line = line[1:-1]
        st.stack.append(tuple(split(line)))
        return ..., None

    if line.endswith(":::["):
        st.tokens.append(T.list)
        st.stack.append([])
        return ..., None

    st.stack.append(line)
    return ..., None

def _do_dicts(n, line, st):
    if line.startswith("}"):
        return st.tokens.pop(), st.value
    else:
        if line.startswith(r"\}"):
            line = line[1:]
        line = line.strip()
        st.value.append(line)
        return ..., None

def _do_graph(n, line, st):
    return ..., None

def _do_directive(n, line, st):
    if line.startswith(">"):
        return st.tokens.pop(), None
    else:
        st.value.append(line)
        return ..., None

class Decoder:
    def __init__(self, commands=None, 
                    meta_directives=None,
                    line_directives=None,
                    value_directives=None, 
                    key_directives=None,
                    struct_directives=None,
                    default_context=None,
                    custom_cases=None):

        self.commands = commands if commands else {}
        self.directives = {
                            D.line: line_directives if line_directives else {},
                            D.key: key_directives if key_directives else {},
                            D.value: value_directives if value_directives else {},
                            D.struct: struct_directives if struct_directives else {},
                            D.meta: meta_directives if meta_directives else {},
                            }
        self.default_context = default_context if default_context else {}
        self.custom_cases = custom_cases if custom_cases else {}

    def __call__(self, lines:Iterator[str], spaces_per_indent=4) -> Iterator[dict]:       
        if isinstance(lines, TextIOBase):
            lines = lines.readlines()

        if not lines:
            return []

        if isinstance(lines, str):
            lines = lines.splitlines()
        
        st = State(self.default_context)
        
        cases = {T.comment: _do_comment,
                T.long: _do_long,
                T.list: _do_list,
                T.dict: _do_dicts,
                T.graph: _do_graph,
                T.start: _do_start,
                T.directive: _do_directive,
                }

        cases.update(self.custom_cases)

        for n, line in enumerate(lines):
            # commands
            if line.startswith("%"):
                parts = [p.strip() for p in line[1:].split("%")]
                if not parts[-1]:
                    raise ParsingError("% denotes the start of a new command, alas none given.")
                
                result = None
                for p in parts:
                    cmd, *args = split(p)
                    try:
                        result = self.commands[cmd](result, *args, 
                            lines=lines, n=n, decoder=self, state=st, cases=cases)
                    except KeyError as e:
                        raise ParsingError("command %s not defined for this Decoder." % (cmd))

                logger.info(line)
                continue

            # directives
            if line.startswith("</"):
                x = line.find(">")
                if x == -1:
                    end = None
                else:
                    end = x
                name, *parts = split(line[2:end])

                for DD, F in self.directives.items():
                    if name in F:
                        del st.directives[DD][name]
                continue

            if line.startswith("<"):
                # allows normal comments after closing
                x = line.find(">")
                if x == -1:
                    end = None
                else:
                    end = x
                name, *args = split(line[1:end])

                if not any(name in d for d in self.directives.values()):
                    logger.info(name, "not specified as any viable directive.")
                else:
                    st.key = [(DD, name, F[name], args)
                            for DD, F in self.directives.items() if name in F]
                if end:
                    try:
                        for DD, name, f, args in st.key:
                            st.directives[DD][name] = f(*args)
                    except TypeError as e:
                        logger.error("Sure the directives are correctly specified in the Decoder?", e)
                else:
                    st.tokens.append(T.directive)
                    st.value = []
                continue
            
            for f in st.directives[D.line].values():
                line = f(line)

            # a short comment
            if line.startswith("#"):
                # long values escape comments
                if st.tokens[-1] is T.long:
                    st.value.append(line)
                
                if line.startswith("###"):
                    # we may have a single "### heading ###"
                    parts = line.split()
                    if len(parts) > 1 and parts[-1] == "###":
                        pass
                    elif st.tokens[-1] is not T.comment:
                        st.tokens.append(T.comment)
                    else:
                        st.tokens.pop()
                continue

            token, data = cases[st.tokens[-1]](n, line, st)

            if token is T.directive:
                for DD, name, f, args in st.key:
                    st.directives[DD][name] = f(*args, s=st.value)
                continue

            if token is ...:
                continue
            
            if data is not None:
                for f in st.directives[D.struct].values():
                    data = f(token, data)
                st.doc[st.key] = data
                continue

            if (line.isspace() or not line):
                continue

            # one might use more than 3 for aesthetics
            if line.startswith("===") or line.startswith("---"):
                if st.tokens[-1] is T.key:
                    raise ParsingError(f"Key {st.key} but no value given.")
                if len(st.tokens) > 1:
                    raise ParsingError(f"Syntax error? Stack: {st.tokens}")
                yield st.doc
                st.doc = {}
                continue

            k, _, v = line.partition(":")
            for f in st.directives[D.key].values():
                k = f(k)

            if isinstance(k, str):
                if k.endswith('"'):
                    k = k[:-1].leftstrip()
                else:
                    k = k.strip()

            # need to add a leading " if spaces must not be ignored

            for f in st.directives[D.value].values():
                v = f(v)
            
            if not isinstance(v, str):
                st.doc[k] = v
                continue

            if v.startswith('"'):
                v = v[1:]
            else:
                v = v.strip()
            
            if v == "::":
                st.tokens.append(T.long)
                st.value = []
                st.key = k.strip()
                continue
            
            if v == "::[":
                st.tokens.append(T.list)
                st.key = k.strip()
                st.stack = []
                continue

            if v == "::{":
                st.tokens.append(T.graph)
                st.value = {}
                st.key = k.strip()
                continue
            
            for x in range(abs(level(line, spaces_per_indent) - len(st.dict_stack))):
                prev, prev_k = st.dict_stack.pop()
                prev[prev_k] = st.doc
                st.doc = prev

            if v == "":
                st.dict_stack.append((st.doc, k))
                st.doc = {}
            else:
                # this implements a list of values, just use "[1 2 3 'foo bar' baz]" to get ['1','2','3', "foo bar", 'baz']
                if v.startswith("[") and v.endswith("]"):
                    v = v[1:-1]
                    v = split(v)
                    token = T.list
                else:
                    # everything else are simple values
                    token = T.simple

                for f in st.directives[D.struct].values():
                    v = f(token, v)
                st.doc[k] = v

        for _ in range(len(st.dict_stack)):
            prev, prev_k = st.dict_stack.pop()
            prev[prev_k] = st.doc
            st.doc = prev

        yield st.doc


class Encoder:
    def __call__(self, it:Union[Iterable, Dict, dataclass], spaces_per_indent=4):
        """Process an iterator of dictionaries as STAY documents, without comments.
        On second thought, it would be cool to auto-add comments, making the file self-documenting.
        """
        it = [it] if isinstance(it, dict) else it
        it = [asdict(it)] if is_dataclass(it) else it
        
        output = "===\n".join(self.__process(asdict(D) if is_dataclass(D) else D) for D in it)
        return output

    def __process(self, D:dict, level=0, spaces_per_indent=4):
        def do(k, v):
            if not isinstance(v, Iterable) or (isinstance(v, str) and "\n" not in v):
                line = f"{' ' * level * spaces_per_indent}{k}: {v}\n"

            elif isinstance(v, str) and "\n" in v:
                line = f"{' ' * level * spaces_per_indent}{k}:::\n{v}\n:::\n"

            elif isinstance(v, Iterable) and not isinstance(v, dict):
                line = f"{' ' * level * spaces_per_indent}{k}: [{' '.join(str(x) for x in v)}]\n"

            elif isinstance(v, dict):
                line = f"{' ' * level * spaces_per_indent}{k}:\n"
                for k, v in v.items():
                    line += '\n'.join(str(x) for x in __process(k, v, level=level+1))
            else:
                raise UserWarning
            return line
        
        text = ''.join(do(k, v) for k, v in D.items())
        return text