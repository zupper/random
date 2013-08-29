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

def exit_error(reason):
	print "Don't know what happened, see the reason below:"
	print reason
	print "Exitting..."
	
	exit(1)

if len(sys.argv) < 3:
	print "You must get an OAuth access token first! Run fblogin.py and check your browser's URL to find it."
	print "Then, you still need your PHPSESSID for mousehuntgame.com - check your HTTP headers for that."
	print ""
	print "USAGE: horn.py [PHPSESSID] [FBConnectAccessToken]"
	print "EXAMPLE: ./horn.py  2edaf334234abc523fgaa444  AQCH-YuVzAi2YhMLLMLfct.....too-long-to-paste........d2fct"
	exit(1)

delay_min = 2
delay_max = 90

sessionid = sys.argv[1]
access_token = sys.argv[2]
turn_url = "https://www.mousehuntgame.com/api/action/turn/me"
user_agent = "Mozilla/5.0 (Linux; U; Android 2.3.3; en-en; HTC Desire Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"

cmd = """curl -s -d 'v=2&client_id=Cordova%%3AAndroid&client_version=0.11.4&game_version=v44320&access_token=%s'""" \
				  """ -b PHPSESSID=%s""" \
				  """ -H 'User-Agent: %s'""" \
				  """ -H 'Accept: application/json, text/javascript, */*; q=0.01'""" \
				  """ -H 'Content-Type: application/x-www-form-urlencoded'""" \
				  """ -H 'X-Requested-With: com.hitgrab.android.mousehunt'""" \
				  """ -H 'Accept-Language: en-US'""" \
				  """ -H 'Accept-Charset: utf-8, iso-8859-1, utf-16, *;q=0.7'""" \
				  """ %s""" % (access_token, sessionid, user_agent, turn_url)

random.seed()

while True:
	response =  os.popen(cmd).read().split("\r\n")
	for line in response:
		if line.startswith("{"):
			response = line
	data = json.loads(response)
	if "user" in data and "next_activeturn_seconds" in data['user'] and data['user']['next_activeturn_seconds'] == 0:
		# we're probably out of bait
		exit_error("Probably no bait in trap. Exiting to avoid detection.")
	
	elif "error" in data and data['error']['code'] == 400:
		# user hunted recently, we have to wait more
		next_delay = random.randint(delay_min, delay_max) + data['user']['next_activeturn_seconds']
		print("[E] (400): User has hunted recently. Time until horn: %d, will sound in: %d" % (data['user']['next_activeturn_seconds'], next_delay))
	
	elif "user" in data:
		# hunt should have been successful, set the delay for next time
		next_delay = random.randint(delay_min, delay_max) + data['user']['next_activeturn_seconds']
		print("[I]: Horn sounded. Status: %s. Will sound in: %d" % (data['user']['trap']['last_activity']['class_name'], next_delay))
	else:
		# we don't know what happened, better stop altogether
		exit_error(response)
		
	time.sleep(next_delay)


