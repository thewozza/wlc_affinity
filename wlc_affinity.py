import csv
from netmiko import ConnectHandler
import os
import subprocess
import re

# these are just simple python formatted files with variables in them
from credentials import *
from controller import *

# this script sets the WLC affinity for all APs on the controller
# it is designed to be as quiet as possible, because I'm running
# it in a crontab

# this loads the devices we're working with from a simple CSV file
# I often alter this file depending on what I'm working on, but my use 
# for this script it to run it under crontab so for me it will always
# be the same contents
devices = csv.DictReader(open("devices.csv"))

for row in devices:
	# first we test if the system is pingable - if it isn't we go to the next one
	# this is a very simple error handling mechanism - the script will crash if it can't reach a host
	response = os.system("ping -c 1 -w2 " + row['IP'] + " >/dev/null 2>&1")
	
	if response == 0:
		# this initializes the device object
		# it pulls the username/password/secret variables from a local file called 'credentials.py'
		# the IP is pulled from the 'devices.csv' file
		cisco_controller = {
		    'device_type': 'cisco_wlc',
		    'ip': row['IP'],
		    'username': username,
		    'password': password,
		    'port' : 22,          # optional, defaults to 22
		    'secret': secret,     # optional, defaults to ''
		    'verbose': False,       # optional, defaults to False
		}
		
		# this actually logs into the device
		net_connect = ConnectHandler(**cisco_controller)
		
		# and here we get a list of APs
		ap_summary = net_connect.send_command('show ap summary').split("]")
		
		# that list is human formatted, so there's some extra stuff we have to filter out
		# I look for the first line with a hyphen '-' and that tells me that the next line will 
		# start the AP list
		# so we SKIP every line until we see a hyphen '-'
		begin = 0
		for ap in ap_summary:
			if begin == 1:
				ap = re.sub("\s\s+", " ", ap)	# strip out the many spaces in between words
				
				# strip out leading and trailing whitespace, and then split into an array using space as a delimeter
				ap_parts = ap.strip().split(" ")
				
				if ap_parts[0]:	# this array element is the AP name (that's what we want) so if it is 
						# defined we can use it
						
					# we pre-set the actual command we're going to send to the controller
					command = [ 'config ap primary-base '+controller+' '+ap_parts[0]+' '+controller_ip ]
					
					# and then we do it
					net_connect.send_config_set(command)
					
			elif "-" in ap:	# if we see a hyphen '-' then we know that we can begin looking at APs
				begin = 1
	else:	# this only happens if we can't ping the device
		print row['Controller'] + "," + row['IP'] + ',down'


