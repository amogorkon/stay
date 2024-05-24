from enum import Enum
from basic import Methods

DRV = Enum("DRV", "line CAP")
STAGE = Enum("Stage", "line key value struct")

directives = set()

hooks = {STAGE.line:}

def loads(lines, hooks=hooks):
	for n, line in enumerate(lines):
		for x in directives
		if (l:=line).startswith("%"):
			for x in line[1:].split():
				if x.startswith("+"):
					directives.add(DRV[x[1:]])
				if x.startswith("-"):
					directives.remove(DRV[x[1:]])
		print(directives)

