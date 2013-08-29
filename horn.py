#!/usr/bin/python

# Author: shade (Copyright C 2013)
#
# License: http://www.wtfpl.net/txt/copying/

import json, random, time, os, sys
from datetime import datetime
import urllib, httplib, webbrowser
from subprocess import call

# delays min/max values below
delay_min = 2
delay_max = 60
tourney_delay_min = 1
tourney_delay_max = 20
big_delay_min = 3600
big_delay_max = 4800
small_delay_min = 450
small_delay_max = 1800

# we keep track of big and small delays to avoid having
# them consecutively or within a time frame
min_horns_between_big_delay = 10
min_horns_between_small_delay = 4
last_big_delay_horns_elapsed = 0;
last_small_delay_horns_elapsed = 0;

def get_access_token():
	LOGIN_URL = "https://m.facebook.com/login.php?skip_api_login=1&api_key=10337532241&signed_next=1&next=https%3A%2F%2Fm.facebook.com%2Fdialog%2Foauth%3Fredirect_uri%3Dfbconnect%253A%252F%252Fsuccess%26display%3Dtouch%26type%3Duser_agent%26client_id%3D10337532241%26ret%3Dlogin&cancel_uri=fbconnect%3A%2F%2Fsuccess%3Ferror%3Daccess_denied%26error_code%3D200%26error_description%3DPermissions%2Berror%26error_reason%3Duser_denied&display=touch&_rdr"
	LOCAL_FILE = '.fb_access_token'
	
	if not os.path.exists(LOCAL_FILE):
		print "Logging you in to facebook..."
		webbrowser.open(LOGIN_URL)
		ACCESS_TOKEN = raw_input('Access Token: ')
		open(LOCAL_FILE,'w').write(ACCESS_TOKEN)
		print "Token saved for future use"
		print ""
	else:
		ACCESS_TOKEN = open(LOCAL_FILE).read()
	
	return ACCESS_TOKEN

def tprint (text):
	time = datetime.now().strftime("%H:%M:%S")
	print "[%s] %s" % (time, text)

def exit_error(reason):
	print "Don't know what happened, see the reason below:"
	print reason
	tprint("Exitting...")
	
	exit(1)

def get_next_delay(time_to_horn):
	global last_big_delay_horns_elapsed, last_small_delay_horns_elapsed
	global min_horns_between_big_delay, min_horns_between_small_delay
	
	# if we're in tourney, sound quicker than usual and never forget
	if tourney_mode:
		return random.randint(tourney_delay_min, tourney_delay_max) + time_to_horn

	# 5% chance to not sound horn for an hour or more (forgot to sound)
	if (random.randint(0, 1000) < 50 and last_big_delay_horns_elapsed >= 0):
		last_big_delay_horns_elapsed = -min_horns_between_big_delay;
		return random.randint(big_delay_min, big_delay_max) + time_to_horn
		
	# 20% chance to delay horn up to half an hour (delayed sound)
	elif (random.randint(0, 1000) < 200 and last_small_delay_horns_elapsed >= 0):
		last_small_delay_horns_elapsed = -min_horns_between_small_delay;
		return random.randint(small_delay_min, small_delay_max) + time_to_horn
		
	# by default, sound as usual
	else:
		last_big_delay_horns_elapsed += 1
		last_small_delay_horns_elapsed += 1
		return random.randint(delay_min, delay_max) + time_to_horn

if len(sys.argv) < 2:
	print ""
	print "You must get an OAuth access token first! Run fblogin.py and check your browser's URL to find it."
	print "Then, you still need your PHPSESSID for mousehuntgame.com - check your HTTP headers for that."
	print ""
	print "USAGE: horn.py [tourney|notourney] [FBConnectAccessToken]"
	print "EXAMPLE: ./horn.py tourney"
	print ""
	exit(1)

# params handling
tourney_mode = sys.argv[1] == 'tourney'
access_token = get_access_token()
sessionid = "orcon308n0vkdpo4orjrb6p4m4" # hardcoded for credibility

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

if tourney_mode:
	print ""
	print "-- Hunting in tourney mode! --"
	print ""

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
		next_delay = get_next_delay(data['user']['next_activeturn_seconds'])
		tprint("[E] (400): User has hunted recently. Time until horn: %d, will sound in: %d" % (data['user']['next_activeturn_seconds'], next_delay))
	
	elif "user" in data:
		# hunt should have been successful, set the delay for next time
		next_delay = get_next_delay(data['user']['next_activeturn_seconds'])
		tprint("[I]: Horn sounded. Status: %s. Will sound in: %d" % (data['user']['trap']['last_activity']['class_name'], next_delay))
	else:
		# we don't know what happened, better stop altogether
		exit_error(response)
		
	time.sleep(next_delay)


