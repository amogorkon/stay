import os, sys
here = os.path.split(os.path.abspath(os.path.dirname(__file__)))
src = os.path.join(here[0], "src/stay")
sys.path.insert(0,src)
from pprint import pprint

from stay import Decoder, __version__, T
import directives as drv
from shlex import split


print(__version__)

decode = Decoder(custom_cases={T.simple: lambda n, value, st: "bla"},
				struct_directives={"list_to_set": drv.list_to_set})

s = """
<list_to_set>
set: [1 2 2 3]
foo: bar
"""

pprint(list(decode(s)))