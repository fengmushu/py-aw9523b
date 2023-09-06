#!/usr/bin/env python3
#coding=utf-8

import argparse
import logging

from usbtty_geehy import *
from attenuator import *

log = logging.getLogger("SatRunner")
logging.basicConfig(level=logging.INFO)

ATTEN_TYPE_HP33321SX	=	0
ATTEN_TYPE_ADAURA	=	1
DEF_ATTEN_TYPE		=	ATTEN_TYPE_ADAURA

DEF_STA_ADDRESS		=	"192.168.10.200"
DEF_STA_PASSWD		=	"admin"

class sat_runner(object):
	def __init__(self) -> None:
		pass

	def process_options(self):
		''' command line options '''
		parser = argparse.ArgumentParser(usage="""psat_runner <cmd> <--args>""",
					description=""" support continue and step down mode """, epilog=""" author: martin """)
		
		parser.add_argument("--atten-start", dest="atten_start", type=int, default=0, help="attenuator start value")
		parser.add_argument("--atten-step", dest="atten_step", type=int, default=5, help="attenuator step down value")
		parser.add_argument("--atten-stop", dest="atten_stop", type=int, default=60, help="attenuator stop value")
		parser.add_argument("--atten-intv", dest="atten_intv", type=int, default=2, help="attenuator step wait intval, sec")
		parser.add_argument("--atten-precision", dest="atten_precision", type=int, default=10, help="flow statistic samples/intval")
		parser.add_argument("--continue", dest="continue_sec", type=int, default=0, help="continue test mode or use step down")
		parser.add_argument("--atten-value", dest="atten_value", type=int, default=15, help="continue mode, the value of attenuator")
		parser.add_argument("--atten-type", dest="atten_type", type=int, default=DEF_ATTEN_TYPE, help="attenuator type: 0 - HP33321SX, 1 - ADAUARA-63")

		parser.add_argument("--angles", dest="rota_angles", type=int, nargs="*", default=0, 
			help="set the angle to rotate,  <point: 0 1 2 3 4 ... 11> or <angle: 0 30 60 90 ... 360>: from 0-360°, each step 30°")

		parser.add_argument("--sta-address", dest="sta_address", type=str, default=DEF_STA_ADDRESS, help="wlan station ip address")
		parser.add_argument("--sta-passwd", dest="sta_passwd", type=str, default=DEF_STA_PASSWD, help="wlan station webui passwd")

		self.args = parser.parse_args()

	def init_attenuators(self):
		if self.args.atten_type == ATTEN_TYPE_HP33321SX:
			serial = tty_usb_geehy(None)
			atten_sc = atten_unit("HP33321-SC", 3, [20, 40, 10])
			atten_sd = atten_unit("HP33321-SD", 3, [30, 40, 5])
			atten_sg = atten_unit("HP33321-SG", 3, [20, 5, 10])
			# init group
			atten_gp_sc_sg = atten_group("SC-SG", serial, [atten_sg, atten_sc])
			self.atten = atten_gp_sc_sg
			self.atten_base_value = 15
			self.atten.dump()
		elif self.args.atten_type == ATTEN_TYPE_ADAURA:
			# Adaura-63: 0-63db, 0.5db step
			self.atten = atten_adaura("ADAURA-63", None)
			self.atten_base_value = 10
			self.atten.dump()
		else:
			print("Not supported attenuator: {}".format(atten))
			raise Exception("Attenuator type '{}' not supported".format(atten))

	def init_sta_rpc(self):
		''' setup OpenWrt rpc '''
		from openwrt_luci_rpc import OpenWrtRpc

		try:
			router = OpenWrtRpc(self.args.sta_address, 'root', self.args.sta_passwd)
			if not router.is_logged_in():
				log.error("OpenWrt rpc: login failed")
				return False
		except Exception as e:
			log.error("OpenWrt rpc link failed")
			return False

		# hosts = router.get_all_connected_devices()
		# print("\n", hosts)
		self.rpc_router = router
		self.current_band = 'ath16'
		return True

	def init_rotary(self):
		''' tty_dio_rotray '''
		self.rotate = tty_dio_rotray(None)

	def init(self):
		''' prepare runner '''
		self.init_attenuators()
		self.init_rotary()
		if self.init_sta_rpc() != True:
			raise Exception("OpenWrt wlan sta RPC connection failed")
		
	def stat_snap_short(self, tv):
		# limit update rate
		# if tv % 5 == 0:
				# self.trex_client._show_global_stats()
		# collection stats
		# stats = self.trex_client.get_stats(ports=[2, 3], sync_now=True)
		# stats = self.trex_client.get_stats(sync_now=True)
		# self.json_dump(stats['global']) --- trace
		# stats = self.trex_client.get_stats(ports=[0, 1, 2, 3], sync_now=True)
		# rx samples to Mbps
		# bps = int(stats['global']['rx_bps'] / 1000000)
		# return bps
		trx = self.rpc_router.get_trx()
		return trx

	def update_rssi(self):
		rssi = -127
		if self.rpc_router != None:
			rssi = self.rpc_router.get_rssi(self.current_band)
			if rssi < -90:
				if self.current_band == 'ath16':
					self.current_band = 'ath06'
				else:
					self.current_band = 'ath16'
				rssi = self.rpc_router.get_rssi(self.current_band)
		return rssi

	def run_samples(self, samples, intval):
		rx_bps = []
		for tv in range(0, samples, 1):
			rx_bps.append(self.stat_snap_short(tv))
			time.sleep(intval)
		return rx_bps

	def run_point_atten(self):
		''' reset to default, waiting for ready '''
		start = self.args.atten_start
		step = self.args.atten_step
		stop = self.args.atten_stop
		intval = self.args.atten_intv
		cont = self.args.continue_sec
		atten_def = self.args.atten_value,
		precision = self.args.atten_precision

		print("Reset default atten...")
		self.atten.set_group_value(atten_def)
		time.sleep(15)

		col_rxbps = {}
		if cont == 0:
			for av in range(start, stop, step):
				self.atten.set_group_value(av)
				rx_bps = self.run_samples(precision, intval / precision)
				col_rxbps.update({self.atten_base_value + av: [rx_bps[:], self.update_rssi()]})
		else:
			for sp in range(0, cont, precision):
				print("Sample round: {}".format(sp), color='red')
				rx_bps = self.run_samples(precision, 1)
				col_rxbps.update({sp: [rx_bps[:], self.update_rssi()]})
		return col_rxbps

	def run(self):
		if self.args.continue_sec > 0:
			log.info("Continue mode {} sec, with atten {}".format(self.args.continue_sec, self.args.atten_value))
		else:
			log.info("Step down from {} to {}, step {}".format(self.args.atten_start, self.args.atten_stop, self.args.atten_step))

		atten_value = self.args.atten_value
		if atten_value <= 0:
			atten_value = self.args.atten_start
		
		# transform
		rota_angles = self.args.rota_angles
		if type(rota_angles) == list:
			for idx in range(0, len(rota_angles), 1):
				point = rota_angles[idx]
				if point > 15:
					rota_angles[idx] = self.rotate.get_point(point)
					print("transform {} to {}".format(point, rota_angles[idx]))
		else:
			rota_angles = []

		self.rotate.set_original()
		print("Rotar angles:{}".format(rota_angles))
		ds_rota={}
		if len(rota_angles) == 0:
			samples = self.run_point_atten()
			ds_rota[0] = samples
		else:
			self.rotate.set_value(0)
			time.sleep(5)
			for point in rota_angles:
				angle = self.rotate.get_angle(point)
				print("Rotar to angle: {}".format(angle), color='green', format='bold')
				self.rotate.set_value(point)
				samples = self.run_point_atten()
				ds_rota[angle] = samples
		# finished, resotre default values
		# self.rotate.SetOriginal()
		self.atten.set_group_value(atten_value)
		# self.json_dump(ds_rota) # --- trace
		self.xlsx = ds_rota

if __name__ == '__main__':
	sat = sat_runner()

	sat.process_options()
	sat.init()
	sat.run()
