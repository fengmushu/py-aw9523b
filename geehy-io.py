#!/usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:	BSD-3-Clause

import sys
import os
import serial
import time
from hexdump import hexdump

PORT='/dev/ttyUSB1'

DATA_ioset=[0x3a, 0x1, 0x0, 0xA]
DATA_delay=[0x3c, 0x05, 1, 0x0, 0x64]

DATA_open 	=[0x3b, 	0,1,0,1,0,1, 	0,1,0,1,0,1,]
DATA_min 	=[0x3b, 	1,0,1,0,1,0, 	1,0,1,0,1,0,]
DATA_halt 	=[0x3b, 	1,1,1,1,1,1, 	1,1,1,1,1,1,]

DATA_sc_sd=[
	[0x3b, 	0,1,0,1,0,1,	0,1,0,1,0,1,],	# open
	[0x3b,	1,0,0,1,0,1,	1,0,0,1,0,1,],	# 15db
	[0x3b,	1,0,0,1,0,1,	0,1,0,1,1,0,],	# 25db
	[0x3b,	1,0,0,1,0,1,	1,0,0,1,1,0,],	# 35db
	[0x3b,	0,1,0,1,1,0,	1,0,0,1,0,1,],	# 40db
	[0x3b,	1,0,0,1,0,1,	0,1,1,0,0,1,],	# 45db
	[0x3b,	0,1,0,1,1,0,	0,1,0,1,1,0,],	# 50db
	[0x3b,	1,0,0,1,0,1,	1,0,1,0,0,1,],	# 55db
	[0x3b,	1,0,0,1,0,1,	0,1,1,0,1,0,],	# 65db
	[0x3b,	0,1,0,1,1,0,	1,0,0,1,1,0,],	# 60db
	[0x3b,	0,1,0,1,1,0,	0,1,1,0,0,1,],	# 70db
	[0x3b,	1,0,0,1,0,1,	1,0,1,0,1,0,],	# 75db
	[0x3b,	0,1,1,0,0,1,	0,1,1,0,0,1,],	# 80db
	]

# SX_MA=0x2A	# b101010

# SC_10=0x29	# b101001
# SC_20=0x1A	# b011010
# SC_30=0x19	# b011001
# SC_40=0x26	# b100110
# SC_50=0x25	# b100101
# SC_60=0x16	# b010110
# SC_70=0x15	# b010101

# SD_05=0x29	# b101001
# SD_30=0x1A	# b011010
# SD_35=0x19	# b011001
# SD_40=0x26	# b100110
# SD_45=0x25	# b100101
# SD_70=0x16	# b010110
# SD_75=0x15	# b010101

# SG_05=0x26	# b100110
# SG_10=0x29	# b101001
# SG_15=0x25	# b100101
# SG_20=0x1A	# b011010
# SG_25=0x16	# b010110
# SG_30=0x19	# b011001
# SG_35=0x15	# b010101

def self_test(ser):
	ser.write(DATA_min)
	time.sleep(1)
	ser.write(DATA_open)
	time.sleep(1)
	ser.write(DATA_halt)

if __name__ == '__main__':
	if len(sys.argv) > 1:
		PORT = sys.argv[1]

	sys.stdout.write("serial port: {!r}\n".format(PORT))
	sys.argv[1:] = ['-v']

	ser=serial.Serial()
	ser.baudrate=115200
	ser.port=PORT
	ser.xonxoff=0
	ser.rtscts=0
	ser.parity='N'
	ser.bytesize=8

	ser.open()
	self_test(ser)
	# ser.write(DATA_ioset)
	# ser.write(DATA_delay)

	# set open drian
	for step in range(0, 13, 1):
		print(step, hexdump(DATA_sc_sd[step]))
		ser.write(DATA_sc_sd[step])
		time.sleep(0.3)
	
	ser.write(DATA_halt)
	
	ser.close()

