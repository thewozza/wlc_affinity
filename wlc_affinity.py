import csv
from netmiko import ConnectHandler
import os
import subprocess
from credentials import *
from controller import *
import re

devices = csv.DictReader(open("devices.csv"))

rowdict = {}

for row in devices:
	response = os.system("ping -c 1 -w2 " + row['IP'] + " >/dev/null 2>&1")
	if response == 0:
		cisco_controller = {
		    'device_type': 'cisco_wlc',
		    'ip': row['IP'],
		    'username': username,
		    'password': password,
		    'port' : 22,          # optional, defaults to 22
		    'secret': secret,     # optional, defaults to ''
		    'verbose': False,       # optional, defaults to False
		}
		net_connect = ConnectHandler(**cisco_controller)
		ap_summary = net_connect.send_command('show ap summary').split("]")
		begin = 0
		for ap in ap_summary:
			if begin == 1:
				ap = re.sub("\s\s+", " ", ap)
				ap_parts = ap.strip().split(" ")
				if ap_parts[0]:
					command = [ 'config ap primary-base '+controller+' '+ap_parts[0]+' '+controller_ip ]
					net_connect.send_config_set(command)
			elif "-" in ap:
				begin = 1
	else:
		print row['Controller'] + "," + row['IP'] + ',down'


