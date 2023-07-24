#!/usr/bin/env python3
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:	BSD-3-Clause

import sys
import time
import os
import serial
import getopt

DATA_ioset=[0x3a, 0x1, 0x0, 0xA]
DATA_delay=[0x3c, 0x05, 1, 0x0, 0x64]

ds_open 	= [0,1,0,1,0,1, 	0,1,0,1,0,1,]
ds_min 		= [1,0,1,0,1,0, 	1,0,1,0,1,0,]
ds_halt 	= [1,1,1,1,1,1, 	1,1,1,1,1,1,]
ds_oops 	= [0,0,0,0,0,0, 	0,0,0,0,0,0,]

ds_subfix_start = [0, 1, 1]
ds_subfix_stop	= [1, 0, 1]
ds_subfix_init	= [1, 1, 0]
ds_subfix_idle	= [1, 1, 1]

DATA_open 	= [0x3b]
DATA_min 	= [0x3b]
DATA_halt 	= [0x3b]
DATA_oops 	= [0x3b]

DATA_open.extend(ds_open)
DATA_min.extend(ds_min)
DATA_halt.extend(ds_halt)
DATA_oops.extend(ds_oops)

class ttyUsbGeehy(object):
	def __init__(self, ttyX):
		self.serial = serial.Serial()
		self.serial.baudrate=115200
		if ttyX == None:
			ttyX=self.FindttyUSBx()
			print("Found %s" % (ttyX))
			if ttyX == None:
				raise Exception("ttyUSB not Found")
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
		ch341_dir='/sys/bus/usb-serial/drivers/ch341-uart/'
		ttyX = os.popen('[ -d {}  ] && ls {} | grep ttyUSB', 'r'.format(ch341_dir, ch341_dir))
		lines = ttyX.read()
		ttyX.close()
		for line in lines.splitlines(False):
			# print(line)
			return "/dev/" + line
		raise Exception("ttyUSB not found")
	
	def WriteIO(self, ds):
		io_w = [0x3b,]
		io_w.extend(ds)
		print("serial io:", io_w)
		self.serial.open()
		self.serial.write(io_w)
		time.sleep(0.1)
		self.serial.write(DATA_halt)
		time.sleep(0.1)
		self.serial.close()

	def WriteIoRaw(self, ds, delay):
		io_w = [0x3b]
		io_w.extend(ds)
		print("serial io:", io_w)
		self.serial.write(io_w)
		self.serial.flush()
		print("wait... {} sec".format(delay))
		time.sleep(delay)

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

class ttyDioRotary(ttyUsbGeehy):
	def __init__(self, ttyX):
		super(ttyDioRotary, self).__init__(ttyX)

	def value2mask(self, value):
		ds = [0, 0, 0, 0, 0, 0]
		for idx in range(len(ds)-1, -1, -1):
			ds[idx] = (1 - (value % 2))
			value = int(value/2)
		ds.reverse()
		return ds

	def setValue(self, value):
		print("set io to {}".format(value))
		ds = self.value2mask(value)
		# print(ds)
		self.serial.open()

		# stop prev distnation
		ds_lock = ds.copy()
		ds_lock.extend(ds_subfix_stop)
		self.WriteIoRaw(ds_lock, 0.1)

		# to target pos
		ds_start = ds.copy()
		ds_start.extend(ds_subfix_start)
		self.WriteIoRaw(ds_start, 0.1)
		self.serial.close()

	def setOriginal(self):
		print("set rotary original pos")
		self.serial.open()
		ds = self.value2mask(0)
		ds_orig = ds.copy()
		ds_orig.extend(ds_subfix_init)
		self.WriteIoRaw(ds_orig, 0.1)
		self.serial.close()
		time.sleep(3)

	def SetIdle(self):
		self.serial.open()
		ds = self.value2mask(0)

		ds_lock = ds.copy()
		ds_lock.extend(ds_subfix_stop)
		self.WriteIoRaw(ds_lock, 1)

		ds_lock = ds.copy()
		ds_lock.extend(ds_subfix_idle)
		self.WriteIoRaw(ds_lock, 0.1)

		self.serial.close()

def Usage():
	print("USAGE:")
	print("    usbtty_geehy")
	print("\t-v [value], jump to pre-program position [0-12,13,14]")
	print("\t-r, restore to original position")
	print("\tpre-program pos:")
	print("\t 0-12: step 30°")
	print("\t   13: unlock, 14: lock")
	print("\n")

# unit test
if __name__ == '__main__':
	# Ser.FindttyUSBx()

	value = -1
	reset = False
	sleep = False
	argv = sys.argv[1:]
	ttyX = None
	# print(argv)
	try:
		opts, args = getopt.getopt(argv, "D:v:rs")
		for opt, arg in opts:
			if opt in ['-v']:	
				value = int(arg)
			if opt in ['-r']:
				reset = True
			if opt in ['-s']:
				sleep = True
			if opt in ['-D']:
				ttyX = arg
	except:
		Usage()
		exit(-1)

	try:
		Rot = ttyDioRotary(ttyX)
	except:
		exit(-1)

	if reset == True:
		Rot.setOriginal()
	elif sleep == True:
		Rot.setIdle()
	elif value in range(0, 15, 1):
		Rot.setValue(value)
	else:
		Usage()

	