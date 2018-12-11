
from shlex import split
from enum import Enum
from collections.abc import Iterable
from typing import Union, Dict, List



T = Enum("Token", "start key comment long list")
D = Enum("Directive", "")

class ParsingError(Exception):
    pass

class StateMachine:
    def __init__(self, *, states:dict, initial):       
        self.states = {}
        self.states.update(states)
        self.state = initial
        self.previous = initial
    
    def flux_to(self, to_state):
        try:
            if to_state in self.states[self.state]:                
                self.previous = self.state
                self.state = to_state
                return True
            else:
                return False
        except KeyError:
            return False
            
    def __call__(self):
        return self.state

def load(file):
    for x in loads(file.readlines()):
        yield x

def loads(text: List[str], spaces_per_indent=4):   
    Parser = StateMachine(states={T.start:{T.long, T.start, T.key, T.comment, T.list},
                                  T.key: {T.long, T.key, T.comment, T.list},
                                  T.long: {T.long, T.start, T.key, T.comment, T.list},
                                  T.list: {T.long, T.start, T.key, T.comment, T.list},
                                  T.comment: {T.long, T.key, T.comment, T.start, T.list},
                                 },
                        initial=T.start)
    
    current = {}
    stack = []
    current_value = []
    current_key = None
    directives = set()

    def level(l):
        l = l.expandtabs(tabsize=spaces_per_indent)
        return (len(l) - len(l.lstrip()))//spaces_per_indent
    
    for n, l in enumerate(text):                
        # long values escape everything, even empty lines
        if (l.isspace() or not l) and Parser() is not T.long:
            continue
            
        # a short comment
        if l.startswith("#"):
            # long values escape comments
            if Parser() is T.long:
                current_value.append(l)
                continue
                
            if l.startswith("###"):
                # we may have a single "### heading ###"
                if len(l.split()) > 2 and l.endswith("###"):
                    continue
                elif Parser() is not T.comment:
                    Parser.flux_to(T.comment)
                else:
                    Parser.flux_to(Parser.previous)
            continue
        
        if Parser() is T.comment:
            continue
        
        if Parser() is T.long:
            if l.startswith(":::"):
                current[current_key] = "\n".join(current_value)
                Parser.flux_to(Parser.previous)
            else:
                # to escape ::: in a long value, everything else already is escaped
                if l.startswith("\:::"):
                    l = l[1:]
                current_value.append(l.rstrip('\n'))
            continue
        
        if Parser() is T.list:               
            if l.startswith("]:::"):
                current[current_key] = current_value
                Parser.flux_to(Parser.previous)
                continue
            
            if l.startswith("\]:::"):
                    l = l[1:]
            
            l = l.strip()

            # like a matrix
            if l.startswith("[") and l.endswith("]"):
                l = l[1:-1]
                l = split(l)

            current_value.append(l)
            continue
             
        # one might use more than 3 for aesthetics
        if l.startswith("===") or l.startswith("---"):
            Parser.flux_to(T.start)
            yield current
            current = {}
            continue
        
        if l.startswith("%"):
            D = split(l[1:])
            for x in D:
                if x.startswith("+"):
                    try:
                        d = getattr(D, x[1:])
                        directives.add(d)
                    except AttributeError:
                        raise ParsingError(f"No such directive: {x} (line {n})")
                elif d.startswith("-"):
                    try:
                        d = getattr(D, x[1:])
                        directives.discard(d)
                    except AttributeError:
                        raise ParsingError(f"No such directive: {x} (line {n})")
            continue
        
        k, _, v = l.partition(":")
        k, v = k.strip(), v.strip()
        
        if v == "::":
            Parser.flux_to(T.long)
            current_value = []
            current_key = k.strip()
            continue
        
        if v == "::[":
            Parser.flux_to(T.list)
            current_value = []
            current_key = k.strip()
            continue
        
        for x in range(abs(level(l) - len(stack))):
                prev, prev_k = stack.pop()
                prev[prev_k] = current
                current = prev
        
        if v == "":
            stack.append((current, k))
            current = {}
        else:
            # this implements a list of values, just use "[1 2 3 'foo bar' baz]" to get [1,2,3, "foo bar", baz]
            if v.startswith("[") and v.endswith("]"):
                v = v[1:-1]
                v = split(v)
            
            # simple values
            current[k] = v
    
    for _ in range(len(stack)):
        prev, prev_k = stack.pop()
        prev[prev_k] = current
        current = prev

    yield current
    
def __process(k, v, level=0, spaces_per_indent=4):
    if not isinstance(v, Iterable) or (isinstance(v, str) and "\n" not in v):
        l = f"{' ' * level * spaces_per_indent}{k}: {v}\n"

    elif isinstance(v, str) and "\n" in v:
        l = f"{' ' * level * spaces_per_indent}{k}:::\n{v}\n:::\n"

    elif isinstance(v, Iterable) and not isinstance(v, dict):
        l = f"{' ' * level * spaces_per_indent}{k}: [{' '.join(str(x) for x in v)}]\n"

    elif isinstance(v, dict):
        l = f"{' ' * level * spaces_per_indent}{k}:\n"
        for k, v in v.items():
            l += '\n'.join(str(x) for x in __process(k, v, level=level+1))
    else:
        raise UserWarning

    yield l

import sys
from packaging import version
if not version.parse(sys.version) >= version.parse("3.7"):
    def dumps(it:Union[Iterable, Dict], spaces_per_indent=4):
        """Process an iterator of dictionaries as SAY documents, without comments."""
        it = [it] if isinstance(it, dict) else it
        assert isinstance(it, Iterable)
        text = ""
        for D in it:
            assert isinstance(D, dict)
            for k, v in D.items():
                text += '===\n'.join(__process(k, v))
            return text

else:
    def dumps(it:Union[Iterable, Dict, dataclass], spaces_per_indent=4):
        """Process an iterator of dictionaries as SAY documents, without comments."""
        it = [it] if isinstance(it, dict) else it
        it = [asdict(it)] if is_dataclass(it) else it
        
        assert isinstance(it, Iterable)
        text = ""
        
        for D in it:
            if is_dataclass(D):
                D = asdict(D)
            assert isinstance(D, dict)
            for k, v in D.items():
                text += '===\n'.join(__process(k, v))
            
            return text