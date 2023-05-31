#!/usr/bin/env python3
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:	BSD-3-Clause

class AttenUnit(object):
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
