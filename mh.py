#!/usr/bin/python

# Author: shade (Copyright C 2013)
#
# License: http://www.wtfpl.net/txt/copying/

from settings import Settings

import json, random, time, os, sys
from datetime import datetime
import urllib, httplib, webbrowser
from subprocess import call

class MH:
	turn_url = "https://www.mousehuntgame.com/api/action/turn/me"
	user_agent = "Mozilla/5.0 (Linux; U; Android 2.3.3; en-en; HTC Desire Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
	
	cmd = """curl -s -d 'v=2&client_id=Cordova%%3AAndroid&client_version=0.11.4&game_version={0}&access_token={1}'""" \
				  """ -b PHPSESSID={2}""" \
				  """ -H 'User-Agent: {3}'""" \
				  """ -H 'Accept: application/json, text/javascript, */*; q=0.01'""" \
				  """ -H 'Content-Type: application/x-www-form-urlencoded'""" \
				  """ -H 'X-Requested-With: com.hitgrab.android.mousehunt'""" \
				  """ -H 'Accept-Language: en-US'""" \
				  """ -H 'Accept-Charset: utf-8, iso-8859-1, utf-16, *;q=0.7'""" \
				  """ {4}"""

	game_version = None
	session_id = None
	access_token = None
	game_version = None
	
	# state vars
	last_big_delay_horns_elapsed = 0;
	last_small_delay_horns_elapsed = 0;

	def tprint (self, text):
		time = datetime.now().strftime("%H:%M:%S")
		print "[%s] %s" % (time, text)

	def get_access_token(self):
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

	def get_game_version(self):
		self.tprint("[I] Getting game version...")
		cmd = "curl -s -d 'game_version=null' %s" % "https://www.mousehuntgame.com/api/info"
		response =  os.popen(cmd).read().split("\r\n")
		for line in response:
			if line.startswith("{"):
				response = line
		data = json.loads(response)
	
		if "game_version" in data:
			return data['game_version']
		else:
			print "API responded weirdly: %s" % data
			return None

	def exit_error(self, reason):
		print "Don't know what happened, see the reason below:"
		print reason
		self.tprint("Exitting...")
	
		exit(1)

	def get_next_delay(self, time_to_horn):
	
		# if we're in tourney, sound quicker than usual and never forget
		if self.tourney_mode:
			return random.randint(Settings.tourney_delay_min, Settings.tourney_delay_max) + time_to_horn

		# 5% chance to not sound horn for an hour or more (forgot to sound)
		if (random.randint(0, 1000) < 50 and self.last_big_delay_horns_elapsed >= 0):
			self.last_big_delay_horns_elapsed = -1 * (Settings.min_horns_between_big_delay);
			return random.randint(Settings.big_delay_min, Settings.big_delay_max) + time_to_horn
		
		# 20% chance to delay horn up to half an hour (delayed sound)
		elif (random.randint(0, 1000) < 200 and self.last_small_delay_horns_elapsed >= 0):
			self.last_small_delay_horns_elapsed = -1 * (Settings.min_horns_between_small_delay);
			return random.randint(Settings.small_delay_min, Settings.small_delay_max) + time_to_horn
		
		# by default, sound as usual
		else:
			self.last_big_delay_horns_elapsed += 1
			self.last_small_delay_horns_elapsed += 1
			return random.randint(Settings.delay_min, Settings.delay_max) + time_to_horn
	
	def loop(self):
		if self.tourney_mode:
			print ""
			print "-- Hunting in tourney mode! --"
			print ""

		while True:
	
			response = os.popen(self.cmd).read().split("\r\n")
			for line in response:
				if line.startswith("{"):
					response = line
			open("debug_response", 'w').write(response)		
			data = json.loads(response)
	
			if "error" in data and data['error']['code'] == 80:
				# game has been updated, we have to change the curl command
				new_version_delay = random.randint(50, 100)
				self.tprint("[E] (80) Game has been updated, have to get new game version. Sleeping for %s to simulate restarting the app..." % new_version_delay)
				time.sleep(new_version_delay)
		
				self.game_version = self.get_game_version()
				cmd = """curl -s -d 'v=2&client_id=Cordova%%3AAndroid&client_version=0.11.4&game_version=%s&access_token=%s'""" \
						  """ -b PHPSESSID=%s""" \
						  """ -H 'User-Agent: %s'""" \
						  """ -H 'Accept: application/json, text/javascript, */*; q=0.01'""" \
						  """ -H 'Content-Type: application/x-www-form-urlencoded'""" \
						  """ -H 'X-Requested-With: com.hitgrab.android.mousehunt'""" \
						  """ -H 'Accept-Language: en-US'""" \
						  """ -H 'Accept-Charset: utf-8, iso-8859-1, utf-16, *;q=0.7'""" \
						  """ %s""" % (game_version, access_token, sessionid, user_agent, turn_url)
				next_delay = self.get_next_delay(data['user']['next_activeturn_seconds'])
				self.tprint("[I]: Game version updated. Will sound in: %d" % next_delay)
		
			elif "user" in data and "next_activeturn_seconds" in data['user'] and data['user']['next_activeturn_seconds'] == 0:
				# we're probably out of bait
				self.exit_error("Probably no bait in trap. Exiting to avoid detection.")
	
			elif "error" in data and data['error']['code'] == 400:
				# user hunted recently, we have to wait more
				next_delay = self.get_next_delay(data['user']['next_activeturn_seconds'])
				self.tprint("[E] (400): User has hunted recently. Time until horn: %d, will sound in: %d" % (data['user']['next_activeturn_seconds'], next_delay))
	
			elif "user" in data:
				# hunt should have been successful, set the delay for next time
				next_delay = self.get_next_delay(data['user']['next_activeturn_seconds'])
				self.tprint("[I]: Horn sounded. Status: %s. Will sound in: %d" % (data['user']['trap']['last_activity']['class_name'], next_delay))
			else:
				# we don't know what happened, better stop altogether
				self.exit_error(response)
		
			time.sleep(next_delay)
			
	def __init__(self, tourneymode):
		self.tourney_mode = tourneymode
	
		random.seed()
		
		self.session_id = "%032x" % random.getrandbits(128)
		self.access_token = self.get_access_token()
		
		self.game_version = self.get_game_version()
		
		self.cmd = self.cmd.format(self.game_version, self.access_token, self.session_id, self.user_agent, self.turn_url)
		
		# sleeping for a while to avoid having the two calls performed simultaneously
		initial_delay = random.randint(5, 20)
		self.tprint("[I] Sleeping for %s to avoid having the two calls too close together." % initial_delay)
		time.sleep(initial_delay)
		
		self.tprint("[I] Ready to hunt")
		