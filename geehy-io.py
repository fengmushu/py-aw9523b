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
DATA_ioset=[0x3a, 0x01, 0x0, 0xA]
DATA_batch=[0x3b, 0x01, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x0, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x0A]
DATA_delay=[0x3c, 0x05, 0x1, 0x0, 0x64]

if __name__ == '__main__':
	if len(sys.argv) > 1:
		PORT = sys.argv[1]

	sys.stdout.write("Testing port: {!r}\n".format(PORT))
	sys.argv[1:] = ['-v']

	ser=serial.Serial()
	ser.baudrate=115200
	ser.port=PORT
	ser.xonxoff=0
	ser.rtscts=0
	ser.parity='N'
	ser.bytesize=8

	ser.open()
	# ser.write(DATA_ioset)
	# ser.write(DATA_batch)
	# ser.write(DATA_delay)

	for gpio in range(1, 16, 1):
		ser.write([0x3c, gpio, 0x1, 0x0, 0x64])
		print(gpio)
		print(hexdump(ser.read()))
		time.sleep(3)
	
	x=ser.write([0x3e, 0xff])	#PULL - DN
	print(hexdump(ser.read()))

	time.sleep(1)

	x=ser.write([0x3d, 0xff])	#PULL - UP
	print(hexdump(ser.read()))

	
	ser.close()

