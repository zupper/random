#!/usr/bin/python

# Author: shade (Copyright C 2013)
#
# License: http://www.wtfpl.net/txt/copying/

from settings import Settings
from mhserverresponse import MHServerResponse

import requests
import json, random, time, os, sys
from datetime import datetime
import urllib, httplib, webbrowser
from subprocess import call

class MH:
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
		
		response = requests.post("https://www.mousehuntgame.com/api/info", params={"game_version": "null"})
		
		response =  response.text.split("\r\n")
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
	
	def hunt(self):
		headers = {
			'User-Agent':		'Mozilla/5.0 (Linux; U; Android 2.3.3; en-en; HTC Desire Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
			'Accept':		'application/json, text/javascript, */*; q=0.01',
			'Content-Type':		'application/x-www-form-urlencoded',
			'X-Requested-With':	'com.hitgrab.android.mousehunt',
			'Accept-Language':	'en-US',
			'Accept-Charset':	'utf-8, iso-8859-1, utf-16, *;q=0.7'
		}
		cookies = {
			'PHPSESSID': self.session_id
		}
		params = {
			'v':			'2',
			'client_id':		'Cordova%%3AAndroid',
			'client_version':	'0.11.4',
			'game_version':		self.game_version,
			'access_token':		self.access_token
		}
		
		#turn_url = "http://httpbin.org/post"
		turn_url = "https://www.mousehuntgame.com/api/action/turn/me"
		
		response = requests.post(turn_url, data=params, headers=headers, cookies=cookies)
		
		return response.text
	
	def loop(self):
		
		if self.tourney_mode:
			print ""
			print "-- Hunting in tourney mode! --"
			print ""

		while True:
	
			raw_response = self.hunt()
			open("debug_response", 'w').write(raw_response)
			
			response = MHServerResponse(raw_response)
	
			if response.status == "error":
				error_delay = random.randint(50, 100)
				self.tprint("[E] Server replied wierdly (no JSON). Will retry once. Delay: %d. Raw response:", error_delay)
				print(raw_response)
				time.sleep(error_delay)
				
				raw_response = os.popen(self.cmd).read().split("\r\n")
				for line in raw_response:
					if line.startswith("{"):
						raw_response = line
				open("debug_response", 'w').write(raw_response)
			
				response = MHServerResponse(raw_response)
				
			if response.status == "error":
				self.tprint("[E] No JSON in reply and already retried. Response:")
				print(raw_response)
				self.tprint("[E] Exiting...")
				exit(1)
				
			elif response.status == "update":
				# game has been updated, we have to get the new version
				next_delay = self.get_next_delay(response.data['time_to_horn'])
				
				new_version_delay = random.randint(50, 100)
				self.tprint("[E] Game has been updated, have to get new game version. Sleeping for %s to simulate restarting the app..." % new_version_delay)
				time.sleep(new_version_delay)
		
				self.game_version = self.get_game_version()
				
				self.tprint("[I] Game version updated. Will sound in: %d" % next_delay)
		
			elif not response.data['have_bait']:
				self.exit_error("Out of bait. Exiting to avoid detection...")
				exit(1)
	
			elif response.status == "warn":
				# user hunted recently, we have to wait more
				next_delay = self.get_next_delay(response.data['time_to_horn'])
				self.tprint("[E] Hunted recently. Status: %s. Time until horn: %d, will sound in: %d" % (response.data['catch']['status'], response.data['time_to_horn'], next_delay))
	
			elif response.status == "ok":
				# hunt should have been successful, set the delay for next time
				next_delay = self.get_next_delay(response.data['time_to_horn'])
				self.tprint("[I] Horn sounded. Status: %s. Will sound in: %d" % (response.data['catch']['status'], next_delay))
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
		
		# sleeping for a while to avoid having the two calls performed simultaneously
		initial_delay = random.randint(5, 20)
		self.tprint("[I] Sleeping for %s to avoid having the two calls too close together." % initial_delay)
		time.sleep(initial_delay)
		
		self.tprint("[I] Ready to hunt")
		
