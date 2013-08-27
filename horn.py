#!/usr/bin/python

# Author: shade (Copyright C 2013)
#
# License: http://www.wtfpl.net/txt/copying/

import json
import random
import time
import urllib, httplib
import os
import sys
from subprocess import call

if len(sys.argv) < 2:
	print "You must be logged in both mousehuntgame.com and facebook.com for this to work."
	print ""
	print "Provide your PHPSESSID from mousehuntgame.com as a parameter!"
	print ""
	print "EXAMPLE: ./horn.py 2ad827d6462e67fgad83782gd"
	exit(1)

delay_min = 2
delay_max = 90
delay_horn = 900

sessionid = sys.argv[1]
turn_url = "https://www.mousehuntgame.com/api/action/turn/me"
user_agent = "Mozilla/5.0 (Linux; U; Android 2.3.3; de-ch; HTC Desire Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"

cmd = """curl -s -d '' -b PHPSESSID=%s -H ''""" \
				  """ -H 'User-Agent: %s'""" \
				  """ -H 'Accept: text/plain'""" \
				  """ %s""" % (sessionid, user_agent, turn_url)

random.seed()

while True:
	response =  os.popen(cmd).read()
	data = json.loads(response)
	
	if "error" in data and data['error']['code'] == 400:
		# user hunted recently, we have to wait more
		next_delay = random.randint(delay_min, delay_max) + data['user']['next_activeturn_seconds']
		print("[E] (400): User has hunted recently. Time until horn: %d, will sound in: %d" % (data['user']['next_activeturn_seconds'], next_delay))
	
	elif "user" in data:
		# hunt should have been successful, set the delay for next time
		next_delay = random.randint(delay_min, delay_max) + data['user']['next_activeturn_seconds']
		print("[I]: Horn sounded. Status: %s. Will sound in: %d" % (data['user']['trap']['last_activity']['class_name'], next_delay))
	else:
		# we don't know what happened, better stop altogether
		print "Don't know what happened, see the raw response below:"
		print response
		print "Exitting..."
		
		exit(1)
	time.sleep(next_delay)


