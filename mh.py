#!/usr/bin/python

# Author: shade (Copyright C 2013)
#
# License: http://www.wtfpl.net/txt/copying/

from settings import Settings
from mhserverresponse import MHServerResponse

import requests
import json, random, time, os, sys, getpass
from datetime import datetime
import urllib, httplib, webbrowser
from subprocess import call

class MH:
	game_version = None
	session_id = None
	access_token = None
	game_version = None
	
	username = None
	password = None

	proxies = None

	all_locations = None
	all_bait = None

	cache_dir = "%s/.mh" % os.path.dirname(os.path.realpath(__file__))
	fb_access_token_file = "%s/fb_access_token" % cache_dir
	mh_access_token_file = "%s/mh_access_token" % cache_dir
	bait_json_file = "%s/bait.json" % cache_dir
	locaitons_json_file = "%s/locations.json" % cache_dir
	
	# state vars
	last_big_delay_horns_elapsed = 0;
	last_small_delay_horns_elapsed = 0;

	def tprint (self, text):
		time = datetime.now().strftime("%H:%M:%S")
		print "[%s] %s" % (time, text)
	
	def check_cache_dir(self):
		if not os.path.exists(self.cache_dir):
			# create the directory
			os.makedirs(self.cache_dir)

	def get_fb_token(self, refresh=False):
		login_url = "https://m.facebook.com/login.php?skip_api_login=1&api_key=10337532241&signed_next=1&next=https%3A%2F%2Fm.facebook.com%2Fdialog%2Foauth%3Fredirect_uri%3Dfbconnect%253A%252F%252Fsuccess%26display%3Dtouch%26type%3Duser_agent%26client_id%3D10337532241%26ret%3Dlogin&cancel_uri=fbconnect%3A%2F%2Fsuccess%3Ferror%3Daccess_denied%26error_code%3D200%26error_description%3DPermissions%2Berror%26error_reason%3Duser_denied&display=touch&_rdr"
	
		if refresh or not os.path.exists(self.fb_access_token_file):
			print "Logging you in to facebook..."
			webbrowser.open(login_url)
			access_token = raw_input('Access Token: ')
			open(self.fb_access_token_file,'w').write(access_token)

			print "Token saved for future use"
			print ""
		else:
			access_token = open(self.fb_access_token_file).read()
		
		return access_token

	def perform_login(self, username):
		#login_url = "http://httpbin.org/post"
		login_url = "https://www.mousehuntgame.com/api/login"

		print "Logging you in to MouseHunt..."

		password = getpass.getpass("Pasword: ")

		headers = {
			'User-Agent':		'Mozilla/5.0 (Linux; U; Android 2.3.3; en-en; HTC Desire Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
			'Accept':			'application/json, text/javascript, */*; q=0.01',
			'Content-Type':		'application/x-www-form-urlencoded',
			'X-Requested-With':	'com.hitgrab.android.mousehunt',
			'Accept-Encoding': 	'gzip,deflate',
			'Accept-Language':	'en-US',
			'Accept-Charset':	'utf-8, iso-8859-1, utf-16, *;q=0.7'
		}
		cookies = {
			'PHPSESSID': self.session_id
		}
		params = {
			'v':				'2',
			'client_id':		'Cordova%%3AAndroid',
			'client_version':	'0.12.4',
			'game_version':		self.game_version,
			'account_name':		username,
			'password':			password,
			'login_token':		1
		}

		response = requests.post(login_url, headers=headers, data=params, cookies=cookies, proxies=self.proxies)
		response = json.loads(response.text)

		return response['login_token']

	def get_login_code(self, username, refresh=False):

		if refresh or not os.path.exists(self.mh_access_token_file):
			login_code = self.perform_login(username)

			open(self.mh_access_token_file,'w').write("%s:%s" % (username, login_code))

			print "Token saved for future use"
			print ""

		else:
			contents = open(self.mh_access_token_file).read().rstrip('\r\n').split(":")
			stored_username = contents[0]
			stored_code = contents[1]

			if (stored_username != username):
				login_code = self.perform_login(username)
			else:
				login_code = stored_code

		return login_code

	def get_game_version(self):
		self.tprint("[I] Getting game version...")
		
		headers = {
			'User-Agent':		'Mozilla/5.0 (Linux; U; Android 2.3.3; en-en; HTC Desire Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
			'Accept':			'application/json, text/javascript, */*; q=0.01',
			'Content-Type':		'application/x-www-form-urlencoded',
			'X-Requested-With':	'com.hitgrab.android.mousehunt',
			'Accept-Encoding': 	'gzip,deflate',
			'Accept-Language':	'en-US',
			'Accept-Charset':	'utf-8, iso-8859-1, utf-16, *;q=0.7'
		}

		response = requests.post("https://www.mousehuntgame.com/api/info", data={"game_version": "null"}, proxies=self.proxies, headers=headers)
		session_id = response.cookies["PHPSESSID"]

		response =  response.text.split("\r\n")
		for line in response:
			if line.startswith("{"):
				response = line
		data = json.loads(response)
	
		if "game_version" in data:
			# store the session ID as a by-product
			self.session_id = session_id
			return data['game_version']
		else:
			print "API responded weirdly: %s" % data
			return None

	def get_game_data(self, url):
		headers = {
			'User-Agent':		'Mozilla/5.0 (Linux; U; Android 2.3.3; en-en; HTC Desire Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
			'Accept':			'application/json, text/javascript, */*; q=0.01',
			'Content-Type':		'application/x-www-form-urlencoded',
			'X-Requested-With':	'com.hitgrab.android.mousehunt',
			'Accept-Encoding': 	'gzip,deflate',
			'Accept-Language':	'en-US',
			'Accept-Charset':	'utf-8, iso-8859-1, utf-16, *;q=0.7'
		}
		cookies = {
			'PHPSESSID': self.session_id
		}
		params = {
			'v':				'2',
			'client_id':		'Cordova%%3AAndroid',
			'client_version':	'0.12.4',
			'game_version':		self.game_version,
		}

		response = requests.post(url, headers=headers, data=params, cookies=cookies, proxies=self.proxies)
		response = json.loads(response.text)

		return response

	def get_baits(self, refresh=False):
		items_url = "https://www.mousehuntgame.com/api/get/item/all"

		bait = []

		if refresh or not os.path.exists(self.bait_json_file):

			objects = self.get_game_data(items_url)

			# filter by "classification": "bait" to get only the cheese
			for item in objects:
				if item['classification'] == 'bait':
					bait.append(item)

			open(self.bait_json_file, 'w').write(json.dumps(bait))
		else:
			raw_json = open(self.bait_json_file, 'w'),read()
			bait = json.loads(raw_json)

		return bait

	def get_locations(self, refresh=False):
		locations_url = "https://www.mousehuntgame.com/api/get/environment/all"

		locations = []

		if refresh or not os.path.exists(self.locaitons_json_file):
			locations = self.get_game_data(locations_url)
			open(self.locaitons_json_file, 'w').write(json.dumps(locations))
		else:
			raw_json = open(self.locaitons_json_file, 'w'),read()
			locations = json.loads(raw_json)

		return locations

	def exit_error(self, reason):
		print "Don't know what happened, see the reason below:"
		print reason
		self.tprint("Exitting...")
	
		exit(1)

	def get_next_delay(self, time_to_horn):
	
		# if we're in tourney, sound quicker than usual and never forget
		if self.mode == "tourney":
			return random.randint(Settings.tourney_delay_min, Settings.tourney_delay_max) + time_to_horn
		elif self.mode == "keepalive":
			return random.randint(Settings.keepalive_delay_min, Settings.keepalive_delay_max)

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
			'Accept':			'application/json, text/javascript, */*; q=0.01',
			'Content-Type':		'application/x-www-form-urlencoded',
			'X-Requested-With':	'com.hitgrab.android.mousehunt',
			'Accept-Language':	'en-US',
			'Accept-Charset':	'utf-8, iso-8859-1, utf-16, *;q=0.7'
		}
		cookies = {
			'PHPSESSID': self.session_id
		}
		params = {
			'v':				'2',
			'client_id':		'Cordova%%3AAndroid',
			'client_version':	'0.12.4',
			'game_version':		self.game_version
		}

		# use the apropriate auth
		if self.username is not None:
			params['login_token'] = self.access_token
		else:
			params['access_token'] = self.access_token
		
		#turn_url = "http://httpbin.org/post"
		turn_url = "https://www.mousehuntgame.com/api/action/turn/me"
		
		response = requests.post(turn_url, data=params, headers=headers, cookies=cookies, proxies=self.proxies)

		return response.text
	
	def loop(self):
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
			
			elif response.status == "login":
				self.tprint("[E] Session has expired. Reauthenticating...")
				self.access_token = self.get_fb_token(True)		# refreshing the expired access token
				
				# have a small delay before trying to sound again
				next_delay = random.randint(1, 10)
				
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
			
	def __init__(self, mode, username=None):

		self.mode = mode
		
		print ""
		print "-- Hunting in %s mode! --" % self.mode
		print ""

		if Settings.proxy is not None:
			self.proxies = {
				"https":	Settings.proxy
			}

		random.seed()
		
		self.check_cache_dir()

		self.game_version = self.get_game_version()
		self.all_bait = self.get_baits()
		self.all_locations = self.get_locations()

		# sleeping for a while to avoid having the two calls performed simultaneously
		initial_delay = random.randint(5, 20)
		self.tprint("[I] Sleeping for %s to avoid having the initial calls too close together." % initial_delay)
		time.sleep(initial_delay)

		if username is not None:
			self.username = username
			self.access_token = self.get_login_code(username)
		else:
			self.access_token = self.get_fb_token()
		
		self.tprint("[I] Ready to hunt")
		
