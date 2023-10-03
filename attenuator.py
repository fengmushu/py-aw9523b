#!/usr/bin/env python3
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:	BSD-3-Clause
import time
import serial
from print_color import print

class atten_unit(object):
	ATTEN_MODE_HP33321_SC = "HP33321-SC"
	ATTEN_MODE_HP33321_SD = "HP33321-SD"
	ATTEN_MODE_HP33321_SG = "HP33321-SG"

	ATTEN_UNIT = {
		ATTEN_MODE_HP33321_SC: [20, 40, 10],
		ATTEN_MODE_HP33321_SD: [30, 40, 5],
		ATTEN_MODE_HP33321_SG: [20, 5, 10],
	}
	def __init__(self, model):
		gears=[]
		atten_sw={0: 0,}

		try:
			num_switch = len(self.ATTEN_UNIT[model])
			values = self.ATTEN_UNIT[model]
		except:
			raise Exception("atten unit init, model '{}' not found".format(model))

		for sw in range(0, 2**num_switch, 1):
			bm=2**num_switch
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

		self.num_switch = num_switch
		self.gears = gears
		self.model = model
		self.atten_sw = atten_sw
		self.busy = []

	def dump(self):
		print("{0} gears: {1}".format(self.model, len(self.atten_sw)))
		for gi in self.gears:
			print('{0:2d} {1}'.format(gi, self.atten_sw.get(gi)))
		print("")

	def get_model(self):
		return self.model

	def GetGeers(self):
		return self.gears

	def GetAtten(self, gi):
		return self.atten_sw.get(gi)

class atten_group(object):
	MIN = 15
	MAX = 115
	def __init__(self, serial_number, serial, units):
		self.serial_number=serial_number
		self.units=units
		self.serial=serial
		self.gears=[]
		self.combo={}

		# DEBUG: init step and maps
		# print("{0} have {1} units".format(self.serial_number, len(units)))
		# for au in units:
		# 	au.dump()

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
	def dump(self):
		print("\nAtten units:")
		print("------------------------------")
		for gu in self.units:
			gu.dump()
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

	def set_value(self, value):
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
					print("{0} {1} \t {2}".format(self.units[ui].get_model(), ue, usw))
				value -= ge
				break
		print("------------------------------")

		print("There's", value, "db loss")
		self.serial.WriteIO(dsmu)
		return value

class atten_adaura(object):
	MIN = 0
	MAX = 63
	def __init__(self, model, ttyX):
		self.model = model
		self.serial = serial.Serial()
		if ttyX == None:
			self.serial.port = self.find_tty_usb()
		self.serial.baudrate=115200
		self.serial.xonxoff=0
		self.serial.rtscts=0
		self.serial.parity='N'
		self.serial.bytesize=8
		self.serial.timeout=1

	def find_tty_usb(self):
		import os
		ttyX = os.popen('ls /sys/class/tty/ | grep ttyACM', 'r')
		lines = ttyX.read()
		ttyX.close()
		for line in lines.splitlines(False):
			# print(line)
			return "/dev/" + line
		return None

	# "INFO", "STATUS", "SET", "SAA", "RAMP", "DEFAULT_ATTEN"
	def send_command(self, cmd):
		self.serial.open()
		cmd_code = cmd.encode('utf-8')
		print(cmd_code, color='red')
		self.serial.write(cmd_code)
		while True:
			self.serial.flush()
			rst = self.serial.readline()
			if rst:
				rst = rst.replace(b'\n', b'').replace(b'\r', b'')
				print(rst)
			else:
				print("----------------------------------------")
				break
		self.serial.close()
		return rst

	def dump(self):
		print("{0} info:".format(self.model))
		self.send_command("INFO")
		self.get_status()

	def get_model(self):
		return self.model

	def get_status(self):
		return self.send_command("STATUS")

	# chain: 1, 2, 3, 4
	# value: 0-63
	def set_value(self, chain, value):
		if chain in [1, 2, 3, 4]:
			print("set chain {0} to {1} db".format(chain, value))
			self.send_command("SET {} {}".format(chain, value))
		else:
			print("error: chain must 1-4")

	def set_group_value(self, value):
		# print("set all to {} db".format(value))
		self.send_command("SAA {}".format(value))

	def set_default_value(self, value):
		print("set all {} as power on".format(value))
		self.send_command("DEFAULT_ATTEN {}".format(value))

	# specified attenuator channels in predefined directions
	# chains: "A A E D"; 	--- A: Ascend, D: Descend, E: exclude
	# todo: [A|B|S|D];	--- A: start, B: stop, S: step, D: delay ms
	def SetRAMP(self, chains, start, end, step, delayms):
		print("RAMP [{0}] from {1} to {2} step {3} delay {4} ms".format(chains, start, end, step, delayms))
		self.send_command("RAMP {0} {1} {2} {3} {4}".format(chains, start, end, step, delayms))
