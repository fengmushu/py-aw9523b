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

DATA_ioset=[0x3a, 0x1, 0x0, 0xA]
DATA_delay=[0x3c, 0x05, 1, 0x0, 0x64]

DATA_open 	=[0x3b, 	0,1,0,1,0,1, 	0,1,0,1,0,1,]
DATA_min 	=[0x3b, 	1,0,1,0,1,0, 	1,0,1,0,1,0,]
DATA_halt 	=[0x3b, 	1,1,1,1,1,1, 	1,1,1,1,1,1,]
DATA_oops 	=[0x3b, 	0,0,0,0,0,0, 	0,0,0,0,0,0,]

class AttenGear(object):
	def __init__(self, model, switchs, values):
		gears=[]
		atten_sw={0:0,}

		for sw in range(0, 2**switchs, 1):
			bm=2**switchs
			vi=len(values)-1
			av=[]
			atn=0
			while bm > 0 and vi >= 0:
				# print(bm, vi)
				b = sw & 0x1
				av.append(b)
				av.append(1-b)
				if b > 0:
					atn += values[vi]
				vi -= 1
				sw >>= 1
				bm >>= 1
			# convert sw to bitmap or list
			atten_sw.update({atn: av})
			gears.append(atn)

		gears.sort()

		self.switchs=switchs
		self.gears=gears
		self.model=model
		self.atten_sw=atten_sw
		self.busy=[]

	def Dump(self):
		print(self.model, "gears:", len(self.atten_sw))
		for gi in self.gears:
			print('\t{:02d}'.format(gi), self.atten_sw.get(gi))
		print("")

	def GetModel(self):
		return self.model

	def GetGeers(self):
		return self.gears

	def GetAtten(self, gi):
		return self.atten_sw.get(gi)

class AttenGroup(object):
	def __init__(self, serial_number, serial, units):
		self.serial_number=serial_number
		self.units=units
		self.serial=serial
		self.gears=[]
		self.combo={}

		# init step and maps
		print(self.serial_number, "have", len(units), "unit")
		for au in units:
			au.Dump()

		def __gears_init(self, layers):
			combo=0
			for li in range(0, len(layers), 1):
				combo += layers[li]

			# print("---", combo, ":", layers)
			# TODO: filter some combo
			self.combo.update({combo:layers.copy()})

		layers=[]
		self.travUnits(layers, __gears_init)
		self.gears.extend(self.combo.keys())
		self.gears.sort()
		self.gears.reverse()

		# print(self.gears)
		# print(self.combo)
	def Dump(self):
		print(" Atten group:", self.serial_number, "DUMP")
		print("------------------------------")
		for ge in self.gears:
			print("Gear:", ge, "\t", self.combo[ge])


	def travUnits(self, layers, cb_func):
		li = len(layers)
		if li == len(self.units):
			# end of traval
			cb_func(self, layers)
			return True
		for gv in self.units[li].GetGeers():
			if gv <= 0:
				continue
			layers.append(gv)
			gi = layers[li]
			# print("layer:", li, layers)
			if self.travUnits(layers, cb_func) != True:
				return False
			layers.pop()
		return True

	def SetValue(self, value):
		print("\n==============================")
		print("-",self.serial_number, "Adjust to:", value, "db -\n")
		dsmu=[]
		print("------------------------------")
		for ge in self.gears:
			if value >= ge:
				for ui in range(0, len(self.combo[ge]), 1):
					ue = self.combo[ge][ui]
					usw = self.units[ui].GetAtten(ue)
					dsmu.extend(usw)
					print("", self.units[ui].GetModel(), ue, "\t", usw)
				value -= ge
				break
		print("------------------------------")

		print("There's", value, "db loss")
		self.serial.WriteIO(dsmu)
		return value

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
		self.serial.write(DATA_halt)
		time.sleep(0.1)

	def SetFull(self):
		self.serial.write(DATA_oops)
		time.sleep(0.1)

def UnitTest(ser):
	print("Self unit test action...")
	ser.SetFull()
	time.sleep(1)
	ser.SetHalt()
	time.sleep(1)
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
	atten_sc = AttenGear("HP33321-SC", 3, [20, 40, 10])
	atten_sd = AttenGear("HP33321-SD", 3, [30, 40, 5])
	atten_sg = AttenGear("HP33321-SG", 3, [20, 5, 10])

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