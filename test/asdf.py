
import os, sys
here = os.path.split(os.path.abspath(os.path.dirname(__file__)))
src = os.path.join(here[0], "src/stay")
sys.path.insert(0,src)


def load(file):
    for x in loads(file):
        yield x
        
def loads(text: str, spaces_per_indent=4):
    print(25, text)
    for n, l in enumerate(text):
        print(n, l)
        
with open("test") as f:
    print("?")
    for d in load(f):
        print(19, d)
