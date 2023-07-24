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

class ttyUsbAdaura(object):
	def __init__(self, ttyX):
		self.serial = serial.Serial()
		self.serial.baudrate=115200
		if ttyX == None:
			ttyX=self.FindttyUSBx()
			print("Found %s" % (ttyX))
			if ttyX == None:
				raise Exception("Not an adaura")
		else:
			print("Use {}".format(ttyX))

		self.serial.port=ttyX
		self.serial.xonxoff=0
		self.serial.rtscts=0
		self.serial.parity='N'
		self.serial.bytesize=8
		# self.serial.open()
		# self.serial.write(DATA_halt)
		# self.serial.close()

	def FindttyUSBx(self):
		ttyX = os.popen('ls /sys/class/tty/ | grep ttyACM', 'r')
		lines = ttyX.read()
		ttyX.close()
		for line in lines.splitlines(False):
			# print(line)
			return "/dev/" + line
		return None

	def UnitTest(adaura):
		print("Self unit test action...")
		exit(0)

def Usage():
	print("For example:")
	print("\t./usbtty_adaura.py -D </dev/ttyUSB0> -v 103")
	exit(-1)


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
		serial = ttyUsbAdaura(None)
	except:
		exit(-1)

	print(serial)
	adaura = AttenAdaura("ADAURA-63", serial)

	if unit_test == True:
		UnitTest(adaura)

	adaura.Dump()

	adaura.SetRAMP('A A E D', 10, 63, 1, 500)

	# for v in range(1, 63, 1):
	# 	adaura.SetValueAll(v)
	# 	adaura.GetStatus()
	# 	time.sleep(1)