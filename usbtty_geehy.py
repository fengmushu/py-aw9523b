#!/usr/bin/env python3
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:	BSD-3-Clause

# from trex.pyserial.serial import *
import time
import os
import serial

DATA_ioset=[0x3a, 0x1, 0x0, 0xA]
DATA_delay=[0x3c, 0x05, 1, 0x0, 0x64]

DATA_open 	=[0x3b, 	0,1,0,1,0,1, 	0,1,0,1,0,1,]
DATA_min 	=[0x3b, 	1,0,1,0,1,0, 	1,0,1,0,1,0,]
DATA_halt 	=[0x3b, 	1,1,1,1,1,1, 	1,1,1,1,1,1,]
DATA_oops 	=[0x3b, 	0,0,0,0,0,0, 	0,0,0,0,0,0,]

class SerialttyUSB(object):
	def __init__(self, ttyX):
		self.serial = serial.Serial()
		self.serial.baudrate=115200
		if ttyX == None:
			ttyX=self.FindttyUSBx()
			print("Found %s" % (ttyX))
		else:
			ttyX="/dev/ttyUSB0"
			print("Use default ttyUSB0")

		self.serial.port=ttyX
		self.serial.xonxoff=0
		self.serial.rtscts=0
		self.serial.parity='N'
		self.serial.bytesize=8
		self.serial.open()
		self.serial.write(DATA_halt)
		self.serial.close()
	
	def FindttyUSBx(self):
		ttyX = os.popen('ls /sys/bus/usb-serial/drivers/ch341-uart/ | grep ttyUSB', 'r')
		lines = ttyX.read()
		ttyX.close()
		for line in lines.splitlines(False):
			# print(line)
			return "/dev/" + line
	
	def WriteIO(self, ds):
		io_w=[0x3b,]
		io_w.extend(ds)
		print("serial io:", io_w)
		self.serial.open()
		self.serial.write(io_w)
		time.sleep(0.1)
		self.serial.write(DATA_halt)
		time.sleep(0.1)
		self.serial.close()

	def SetHalt(self):
		print("set io halt...")
		self.serial.open()
		self.serial.write(DATA_halt)
		time.sleep(0.1)
		self.serial.close()

	def SetFull(self):
		print("set io oops...")
		self.serial.open()
		self.serial.write(DATA_oops)
		time.sleep(0.1)
		self.serial.close()

# unit test
if __name__ == '__main__':
	Ser = SerialttyUSB(None)
	Ser.FindttyUSBx()