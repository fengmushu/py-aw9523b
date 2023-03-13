#!/usr/bin/env python

import smbus
import time
import random

bus = smbus.SMBus(1)
addr = 0x5b

AW9523B_P0_IN_STATE 	= 0x00
AW9523B_P1_IN_STATE 	= 0x01
AW9523B_P0_OUT_STATE 	= 0x02
AW9523B_P1_OUT_STATE 	= 0x03
AW9523B_P0_CONF_STATE	= 0x04	# 0b: out, 1b: input
AW9523B_P1_CONF_STATE 	= 0x05

AW9523B_REG_ID		= 0x10
AW9523B_ID		= 0x23

AW9523B_REG_GLOB_CTR	= 0x11
AW9523B_P0_LED_MODE	= 0x12	# 0b: led, 1b: gpio
AW9523B_P1_LED_MODE	= 0x13
AW9523B_REG_SOFT_RST	= 0x7f

DIM_MAX	= 0x00
DIM_MED = 0x01
DIM_LOW	= 0x02
DIM_MIN	= 0x03

P1_0 = 0x20 	# DIM0
P1_1 = 0x21 	# DIM1
P1_2 = 0x22 	# DIM2
P1_3 = 0x23 	# DIM3
P0_0 = 0x24 	# DIM4
P0_1 = 0x25 	# DIM5
P0_2 = 0x26 	# DIM6
P0_3 = 0x27 	# DIM7
P0_4 = 0x28 	# DIM8
P0_5 = 0x29 	# DIM9
P0_6 = 0x2A 	# DIM10
P0_7 = 0x2B 	# DIM11
P1_4 = 0x2C 	# DIM12
P1_5 = 0x2D 	# DIM13
P1_6 = 0x2E 	# DIM14
P1_7 = 0x2F 	# DIM15

OPEN_DRAIN	= 0x0
PUSH_PULL	= 0x8

def aw_write(reg, val):
	bus.write_byte_data(addr, reg, val)

def aw_read(reg):
	return bus.read_byte_data(addr, reg)

def aw_init():
	print("Wait aw9523b reset...")
	aw_write(AW9523B_REG_SOFT_RST, 0x0)
	devid=aw_read(AW9523B_REG_ID)
	print("DevID: ", hex(devid))

	# aw_write(AW9523B_P0_CONF_STATE, 0)
	# aw_write(AW9523B_P1_CONF_STATE, 0)
	aw_write(AW9523B_P0_LED_MODE, 0x00)
	aw_write(AW9523B_P1_LED_MODE, 0x00)
	aw_write(AW9523B_REG_GLOB_CTR, DIM_MIN | OPEN_DRAIN)
	return 0

def aw_dump():
	print("Pin conf, PIN-[0]:", aw_read(AW9523B_P0_CONF_STATE),
                       " PIN-[1]:", aw_read(AW9523B_P1_CONF_STATE))

	print("IO state, IN-[0]:", aw_read(AW9523B_P0_IN_STATE),
	               " IN-[1]:", aw_read(AW9523B_P1_IN_STATE),
                       " OUT-[0]:", aw_read(AW9523B_P0_OUT_STATE),
		       " OUT-[1]:", aw_read(AW9523B_P1_OUT_STATE))
	return 0

def aw_test():
	for i in range(0, 8):
		print("PIN: ", i)
		for brightness in range(0, 255, 50):
			aw_write(P1_0 + i, brightness)
			time.sleep(0.1)
	return 0

def aw_recycle():
	counter=0
	while 1:
		rand = random.randint(20,200)
		aw_write(P1_0, 255)
		print("Power on", counter, " waiting... ", rand, "seconds")
		time.sleep(rand)
		aw_write(P1_0, 0)
		counter = counter + 1
		# time.sleep(3)
		aw_test()
	return


def main():
	aw_init()
	aw_test()
	aw_dump()
	aw_recycle()

if __name__ == "__main__":
    main()