#!/usr/bin/env python3
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:	BSD-3-Clause

import sys
import os
import serial
import time
import getopt
from hexdump import hexdump

from attenuator import AttenUnit, AttenGroup

DATA_ioset=[0x3a, 0x1, 0x0, 0xA]
DATA_delay=[0x3c, 0x05, 1, 0x0, 0x64]

DATA_open 	=[0x3b, 	0,1,0,1,0,1, 	0,1,0,1,0,1,]
DATA_min 	=[0x3b, 	1,0,1,0,1,0, 	1,0,1,0,1,0,]
DATA_halt 	=[0x3b, 	1,1,1,1,1,1, 	1,1,1,1,1,1,]
DATA_oops 	=[0x3b, 	0,0,0,0,0,0, 	0,0,0,0,0,0,]

class SerialttyUSB(object):
	def __init__(self, ser, ttyUSB):
		ser.baudrate=115200
		ser.port=ttyUSB
		ser.xonxoff=0
		ser.rtscts=0
		ser.parity='N'
		ser.bytesize=8
		ser.open()
		ser.write(DATA_halt)
		time.sleep(0.1)
		self.serial=ser
	
	def WriteIO(self, ds):
		io_w=[0x3b,]
		io_w.extend(ds)
		print("serial io:", io_w)
		self.serial.write(io_w)
		time.sleep(0.1)
		self.serial.write(DATA_halt)
		time.sleep(0.1)

	def SetHalt(self):
		print("set io halt...")
		self.serial.write(DATA_halt)
		time.sleep(0.1)

	def SetFull(self):
		print("set io oops...")
		self.serial.write(DATA_oops)
		time.sleep(0.1)

def UnitTest(ser):
	print("Self unit test action...")
	ser.SetFull()
	time.sleep(3)
	ser.SetHalt()
	time.sleep(3)
	exit(0)

def Usage():
	print("For example:")
	print("\t./geehy-io.py -D </dev/ttyUSB0> -v 103")
	exit(-1)

if __name__ == '__main__':
	argv=sys.argv[1:]

	try:
		opts, args = getopt.getopt(argv, "D:v:ts:i:")
	except:
		Usage()

	atten=None
	unit_test=None
	intv_waitting=5
	init_atten=20
	for opt, arg in opts:
		if opt in ['-D']:
			ttyX=arg
		if opt in ['-v']:
			atten=int(arg)
		if opt in ['-t']:
			unit_test = True
		if opt in ['-i']:
			intv_waitting = int(arg)
		if opt in ['-s']:
			init_atten = int(arg)

	try:
		ttyX
	except:
		ttyX='/dev/ttyUSB0'

	Ser = SerialttyUSB(serial.Serial(), ttyX)
	atten_sc = AttenUnit("HP33321-SC", 3, [20, 40, 10])
	atten_sd = AttenUnit("HP33321-SD", 3, [30, 40, 5])
	atten_sg = AttenUnit("HP33321-SG", 3, [20, 5, 10])

	if unit_test == True:
		UnitTest(Ser)

	if atten == None:
		Usage()
	# atten_gp_sc_sg_sd = AttenGroup("SC-SG-SD", Ser, [atten_sc, atten_sg, atten_sd])
	# atten_gp_sc_sg_sd.Dump()
	# atten_gp_sc_sg_sd.SetValue(atten)

	# atten_gp_sc_sg = AttenGroup("SC-SG", Ser, [atten_sc, atten_sg])
	atten_gp_sc_sg = AttenGroup("SC-SG", Ser, [atten_sg, atten_sc])
	atten_gp_sc_sg.Dump()
	atten_gp_sc_sg.SetValue(init_atten)
	time.sleep(10)

	print("\ntarget:", atten, "cut to 5*X =", int(atten / 5) * 5)
	sys.stdout.write(" serial port: {!r}, intv: {:d} sec.\n".format(ttyX, intv_waitting))
	for av in range(init_atten, atten + 5, 5):
		atten_gp_sc_sg.SetValue(av)
		time.sleep(intv_waitting)