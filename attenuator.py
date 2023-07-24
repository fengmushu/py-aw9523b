#!/usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:	BSD-3-Clause
import time
import serial
from print_color import print

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
		print("{0} gears: {1}".format(self.model, len(self.atten_sw)))
		for gi in self.gears:
			print('{0:2d} {1}'.format(gi, self.atten_sw.get(gi)))
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
		print("{0} have {1} units".format(self.serial_number, len(units)))
		for au in units:
			au.Dump()

		def __gears_init(self, layers):
			cbin=0
			for li in range(0, len(layers), 1):
				cbin += layers[li]

			# TODO: filter some cbin
			# print("--- {0:3d} : {1}".format(cbin, layers))
			# self.combo.update({cbin:layers.copy()}) 	# python2.7 not supported
			self.combo.update({cbin: layers[:]})		# use slic

		layers=[]
		self.travUnits(layers, __gears_init)
		self.gears.extend(self.combo.keys())
		self.gears.sort()
		self.gears.reverse()

		# print(self.gears)
		# print(self.combo)
	def Dump(self):
		print("\nAtten units:")
		print("------------------------------")
		for gu in self.units:
			gu.Dump()
		print("\nAtten group: {0} DUMP".format(self.serial_number))
		print("------------------------------")
		for ge in self.gears:
			print("Gear: {0} \t {1}".format(ge, self.combo[ge]))


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
		print("- {0} Adjust to: ${1} db -".format(self.serial_number, value), color='green', format='bold')
		dsmu=[]
		print("------------------------------")
		for ge in self.gears:
			if value >= ge:
				for ui in range(0, len(self.combo[ge]), 1):
					ue = self.combo[ge][ui]
					usw = self.units[ui].GetAtten(ue)
					dsmu.extend(usw)
					print("{0} {1} \t {2}".format(self.units[ui].GetModel(), ue, usw))
				value -= ge
				break
		print("------------------------------")

		print("There's", value, "db loss")
		self.serial.WriteIO(dsmu)
		return value

# "INFO", "STATUS", "SET", "SAA", "RAMP", "DEFAULT_ATTEN"
class AttenAdaura(object):
	def __init__(self, model, Ser):
		self.model = model
		# Ser = serial.Serial()
		self.Ser = Ser

	def send_command(self, cmd):
		self.Ser.open()
		self.Ser.write(cmd.encode('utf-8'))
		while True:
			rst = self.Ser.readline()
			if rst:
				rst = rst.replace(b'\n', b'').replace(b'\r', b'')
				print(rst)
			else:
				break
		self.Ser.close()
		return rst

	def Dump(self):
		print("{0} info:".format(self.model))
		self.send_command("INFO")

	def GetModel(self):
		return self.model

	def GetStatus(self):
		return self.send_command("STATUS")

	# chain: 1, 2, 3, 4
	# value: 0-63
	def SetValue(self, chain, value):
		if chain in [1, 2, 3, 4]:
			print("set chain {0} to {1} db".format(chain, value))
			self.send_command("SET {} {}".format(chain, value))
		else:
			print("error: chain must 1-4")
		
	def SetValueAll(self, value):
		print("set all to {} db".format(value))
		self.send_command("SAA {}".format(value))

	def SetDefaultValue(self, value):
		print("set all {} as power on".format(value))
		self.send_command("DEFAULT_ATTEN {}".format(value))

	# specified attenuator channels in predefined directions
	# chains: "A A E D"; 	--- A: Ascend, D: Descend, E: exclude
	# todo: [A|B|S|D];	--- A: start, B: stop, S: step, D: delay ms
	def SetRAMP(self, chains, start, end, step, delayms):
		print("RAMP [{0}] from {1} to {2} step {3} delay {4} ms".format(chains, start, end, step, delayms))
		self.send_command("RAMP {0} {1} {2} {3} {4}".format(chains, start, end, step, delayms))
