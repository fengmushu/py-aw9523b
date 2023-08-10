#!/usr/bin/env python3
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:	BSD-3-Clause

import sys
import os
import time
import serial
import getopt
from hexdump import hexdump
from attenuator import AttenAdaura
from print_color import print

def Usage():
	print("For example:")
	print("\t./usbtty_adaura.py -D </dev/ttyUSB-X> -v 103")
	print("\t	-v <value>, set all channel to value")
	print("\t	-d <value>, power on default value")
	print("\t	-c <1, 2, 3, 4>, channel to set")
	print("\t	-s <start> -e <stop> -i <step> -w <delay seconds>")
	print("\t	-u unit test")
	exit(-1)

if __name__ == '__main__':
	argv=sys.argv[1:]

	try:
		opts, args = getopt.getopt(argv, "D:us:e:i:w:d:v:c:")
	except:
		Usage()

	unit_test=None
	intv_waitting=2000
	start_value=None
	stop_value=63
	step_value=1
	set_value=None
	default_value=None
	channel=None
	for opt, arg in opts:
		if opt in ['-D']:
			ttyX=arg
		if opt in ['-u']:
			unit_test = True
		if opt in ['-s']:
			start_value = int(arg)
		if opt in ['-e']:
			stop_value = int(arg)
		if opt in ['-i']:
			step_value = int(arg)
		if opt in ['-w']:
			intv_waitting = int(arg) * 1000
		if opt in ['-d']:
			default_value = int(arg)
		if opt in ['-v']:
			set_value = int(arg)
		if opt in ['-c']:
			channel = int(arg)

	try:
		adaura = AttenAdaura("ADAURA-63", None)
	except Exception as e:
		print(e)
		exit(-1)

	# if unit_test == True:
	# 	UnitTest(adaura)

	# adaura.Dump()
	if set_value != None:
		adaura.SetGroupValue(set_value)

	if start_value != None:
		# init
		adaura.SetGroupValue(start_value)
		# A: Ascend
		# E: Exclud
		# D: Descend
		# Start, Stop, Step, Delay
		# !!! BUG: RAMP is not supported ...
		# adaura.SetRAMP('D D A A', start_value, stop_value, step_value, intv_waitting)

		for val in range(start_value, stop_value, step_value):
			if channel != None:
				adaura.SetValue(channel, val)
			else:
				adaura.SetGroupValue(val)
			time.sleep(intv_waitting/1000)

	if default_value != None:
		adaura.SetDefaultValue(default_value)

	adaura.GetStatus()