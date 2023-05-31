#!/usr/bin/env python3
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:	BSD-3-Clause

import serial
import time

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