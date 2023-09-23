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
from print_color import print
from attenuator import *
from usbtty_geehy import *

def UnitTest(ser):
	print("Self unit test action...")
	ser.SetFull()
	time.sleep(3)
	ser.SetHalt()
	time.sleep(1)
	exit(0)

def usage():
	print("For example:")
	print("\t./geehy-io.py -D </dev/ttyUSB0> -v 103")
	exit(-1)

if __name__ == '__main__':
	argv=sys.argv[1:]

	try:
		opts, args = getopt.getopt(argv, "D:v:ut:s:i:w:")
	except:
		usage()

	atten=None
	unit_test=None
	intv_waitting=5
	init_atten=20
	step_lvl=5
	start_wait=3
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
		if opt in ['-w']:
			start_wait = int(arg)

	try:
		ttyX
	except:
		ttyX='/dev/ttyUSB0'

	Ser = tty_usb_geehy(ttyX)
	atten_sc = atten_unit(atten_unit.ATTEN_MODE_HP33321_SC)
	atten_sd = atten_unit(atten_unit.ATTEN_MODE_HP33321_SD)
	atten_sg = atten_unit(atten_unit.ATTEN_MODE_HP33321_SG)

	if unit_test == True:
		UnitTest(Ser)

	if atten == None:
		usage()
	# atten_grp = AttenGroup("SC-SG-SD", Ser, [atten_sc, atten_sg, atten_sd])
	# atten_grp.dump()
	# atten_grp.set_value(atten)

	atten_grp = atten_group("SC-SG", Ser, [atten_sc, atten_sg])
	# atten_grp = atten_group("SC-SD", Ser, [atten_sc, atten_sd])
	atten_grp.dump()
	atten_grp.set_value(init_atten)
	time.sleep(start_wait)

	print("\nTarget: {} cell to 5 * {} = {}".format(atten, int(atten/5), int(atten/5)*5), color = "yellow", background='gray', format='bold')
	sys.stdout.write(" serial port: {!r}, step:{:d} intv: {:d} sec.\n".format(ttyX, step_lvl, intv_waitting))
	for av in range(init_atten, atten + 5, step_lvl):
		atten_grp.set_value(av)
		time.sleep(intv_waitting)