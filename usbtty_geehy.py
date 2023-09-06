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
from hexdump import hexdump

DATA_ioset=[0x3a, 0x1, 0x0, 0xA]
DATA_delay=[0x3c, 0x05, 1, 0x0, 0x64]

ds_open 	= [0,1,0,1,0,1, 	0,1,0,1,0,1,]
ds_min 		= [1,0,1,0,1,0, 	1,0,1,0,1,0,]
ds_halt 	= [1,1,1,1,1,1, 	1,1,1,1,1,1,]
ds_oops 	= [0,0,0,0,0,0, 	0,0,0,0,0,0,]

ewhc_halt 	= [1, 1, 1, 1, 1, 1, 1, 1]
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

POINTS_TO_ANGLES=[1, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 350]

class tty_usb_geehy(object):
	def __init__(self, ttyX):
		self.serial = serial.Serial()
		self.serial.baudrate=115200
		if ttyX == None:
			ttyX=self.find_tty_usb()
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
		self.serial.timeout = 3
		# self.serial.open()
		# self.serial.write(DATA_halt)
		# self.serial.close()
	
	def find_tty_usb(self):
		ch341_dir='/sys/bus/usb-serial/drivers/ch341-uart/'
		ttyX = os.popen("[ -d {}  ] && ls {} | grep ttyUSB".format(ch341_dir, ch341_dir), 'r')
		lines = ttyX.read()
		ttyX.close()
		lines = lines.splitlines(False)
		if len(lines) <= 0:
			raise Exception("ttyUSB not found yet")
		for line in lines:
			# print(line)
			return "/dev/" + line
	
	def WriteIO(self, ds):
		io_w = [0x3b,]
		io_w.extend(ds)
		print("serial io:", io_w)
		self.serial.open()
		self.serial.write(io_w)
		self.serial.flush()
		self.serial.write(DATA_halt)
		self.serial.flush()
		self.serial.close()

	def ReadIoRaw(self, channels):
		rx_o = []
		for ch in channels:
			io_r = [0x3f, ch]
			# print(io_r)
			self.serial.write(io_r)
			self.serial.flush()
			rx = self.serial.read(size=3)
			rx_o.append(rx)
			# time.sleep(1)
		print(rx_o)
		return rx_o

	def write_io_raw(self, ds, delay):
		io_w = [0x3b,]
		io_w.extend(ds)
		print("serial io:", io_w)
		self.serial.write(io_w)
		self.serial.flush()
		# while True:
		# 	TODO: ...
		# print("wait... {} sec".format(delay))
		time.sleep(delay)

	def SetHalt(self):
		print("set io halt...")
		self.serial.open()
		self.serial.write(DATA_halt)
		self.serial.flush()
		self.serial.close()

	def SetFull(self):
		print("set io oops...")
		self.serial.open()
		self.serial.write(DATA_oops)
		self.serial.flush()
		self.serial.close()

class tty_dio_rotray(tty_usb_geehy):
	def __init__(self, ttyX):
		super(tty_dio_rotray, self).__init__(ttyX)

	def __value2mask(self, value):
		ds = [0, 0, 0, 0, 0, 0, 0, 0]
		for idx in range(len(ds)-1, -1, -1):
			ds[idx] = (1 - (value % 2))
			value = int(value/2)
		ds.reverse()
		return ds

	def __point_to_angle(self, point):
		return POINTS_TO_ANGLES[point]

	def __angle_to_point(self, angle):
		return int(angle / 30)

	def get_angle(self, point):
		return self.__point_to_angle(point)

	def get_point(self, angle):
		return self.__angle_to_point(angle)

	def set_value(self, value):
		print("\tio {}".format(value))
		ds = self.__value2mask(value)
		# print(ds)
		self.serial.open()
		# stop prev
		# ds_stop = ewhc_halt.copy()
		# ds_stop.extend(ds_subfix_stop)
		# self.write_io_raw(ds_stop, 0.1)
		# to target pos
		ds_start = ds.copy()
		ds_start.extend(ds_subfix_start)
		self.write_io_raw(ds_start, 1)
		# TODO: wait ready(): 9: Ready, 10: Busy, 11: Inpos, 12: hold
		# stop prev distnation
		ds_pause = ewhc_halt.copy()
		ds_pause.extend(ds_subfix_idle)
		self.write_io_raw(ds_pause, 0.1)
		self.serial.close()

	def set_original(self):
		print("Rotary original pos")
		self.serial.open()
		ds_orig = ewhc_halt.copy()
		ds_orig.extend(ds_subfix_init)
		self.write_io_raw(ds_orig, 3)
		ds_pause = ewhc_halt.copy()
		ds_pause.extend(ds_subfix_idle)
		self.write_io_raw(ds_pause, 0.1)
		self.serial.close()

	def set_idle(self):
		self.serial.open()
		ds_lock = ewhc_halt.copy()
		ds_lock.extend(ds_subfix_idle)
		self.write_io_raw(ds_lock, 0.1)
		self.serial.close()

	def unit_test(self):
		self.set_original()
		for point in range(0, 13, 1):
			self.set_value(point)
		for point in range(12, -1, -1):
			self.set_value(point)
		self.set_original()

		# self.serial.open()
		# self.ReadIoRaw([1, 2, 3, 4, 13, 14, 15, 16])
		# self.serial.close()

		self.set_idle()

def usage():
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
	# Ser.find_tty_usb()

	value = -1
	reset = False
	sleep = False
	argv = sys.argv[1:]
	ttyX = None
	unit_test = None
	# print(argv)
	try:
		opts, args = getopt.getopt(argv, "D:v:rsu")
		for opt, arg in opts:
			if opt in ['-v']:	
				value = int(arg)
			if opt in ['-r']:
				reset = True
			if opt in ['-s']:
				sleep = True
			if opt in ['-D']:
				ttyX = arg
			if opt in ['-u']:
				unit_test = True
	except:
		usage()
		exit(-1)

	try:
		Rot = tty_dio_rotray(ttyX)
	except Exception as e:
		print(e)
		exit(-1)

	if unit_test:
		Rot.unit_test()

	if reset == True:
		Rot.set_original()
	elif sleep == True:
		Rot.set_idle()
	elif value in range(0, 15, 1):
		Rot.set_value(value)
	else:
		usage()

	