#!/usr/bin/env python3
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:	BSD-3-Clause

import sys
import os
import time
import getopt
from hexdump import hexdump
from attenuator import AttenAdaura #AttenUnit, AttenGroup

def UnitTest(ser):
	print("Self unit test action...")
	exit(0)

def Usage():
	print("For example:")
	print("\t./geehy-io.py -D </dev/ttyUSB0> -v 103")
	exit(-1)

def FindttyUSBx():
	ttyX = os.popen('ls /sys/class/tty/ | grep ttyACM', 'r')
	lines = ttyX.read()
	ttyX.close()
	for line in lines.splitlines(False):
		# print(line)
		return "/dev/" + line


if __name__ == '__main__':
	argv=sys.argv[1:]

	try:
		opts, args = getopt.getopt(argv, "D:v:ut:s:i:")
	except:
		Usage()

	atten=None
	unit_test=None
	intv_waitting=5
	init_atten=20
	step_lvl=5
	for opt, arg in opts:
		if opt in ['-D']:
			ttyX=arg
		if opt in ['-v']:
			atten=int(arg)
		if opt in ['-u']:
			unit_test = True
		if opt in ['-i']:
			intv_waitting = int(arg)
		if opt in ['-s']:
			init_atten = int(arg)
		if opt in ['-t']:
			step_lvl = int(arg)

	try:
		ttyX
	except:
		ttyX=FindttyUSBx()

	adaura = AttenAdaura("ADAURA-63", ttyX)

	if unit_test == True:
		UnitTest(Ser)

	adaura.Dump()

	adaura.SetRAMP('A A E D', 10, 63, 1, 500)

	# for v in range(1, 63, 1):
	# 	adaura.SetValueAll(v)
	# 	adaura.GetStatus()
	# 	time.sleep(1)