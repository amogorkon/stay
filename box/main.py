#!/usr/bin/env python3.8

from stay import loads
from basic import Methods

class Method_User(Methods):
	def CAP(line):
		return str.capitalize(line)



loads(open("test.stay"),Method_User)

