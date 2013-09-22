#!/usr/bin/python

# Author: shade (Copyright C 2013)
#
# License: http://www.wtfpl.net/txt/copying/

from settings import Settings
from mhserverresponse import MHServerResponse
import util, os

import requests
import json, random, time, getpass
import webbrowser

class MH:
	game_version = None
	session_id = None
	access_token = None
	game_version = None
	
	username = None
	password = None

	proxies = None

	def get_game_version(self):
		util.tprint("[I] Getting game version...")
		
		response = requests.post("https://www.mousehuntgame.com/api/info", data={"game_version": "null"}, proxies=self.proxies)
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
	
	def get_access_token(self, refresh=False):
		login_url = "https://m.facebook.com/login.php?skip_api_login=1&api_key=10337532241&signed_next=1&next=https%3A%2F%2Fm.facebook.com%2Fdialog%2Foauth%3Fredirect_uri%3Dfbconnect%253A%252F%252Fsuccess%26display%3Dtouch%26type%3Duser_agent%26client_id%3D10337532241%26ret%3Dlogin&cancel_uri=fbconnect%3A%2F%2Fsuccess%3Ferror%3Daccess_denied%26error_code%3D200%26error_description%3DPermissions%2Berror%26error_reason%3Duser_denied&display=touch&_rdr"
		local_file = '.fb_access_token'
	
		if refresh or not os.path.exists(local_file):
			print "Logging you in to facebook..."
			webbrowser.open(login_url)
			access_token = raw_input('Access Token: ')
			open(local_file,'w').write(access_token)

			print "Token saved for future use"
			print ""
		else:
			access_token = open(local_file).read()
		
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
		local_file = '.mh_login_code'

		if refresh or not os.path.exists(local_file):
			login_code = self.perform_login(username)

			open(local_file,'w').write("%s:%s" % (username, login_code))

			print "Token saved for future use"
			print ""

		else:
			contents = open(local_file).read().rstrip('\r\n').split(":")
			stored_username = contents[0]
			stored_code = contents[1]

			if (stored_username != username):
				login_code = self.perform_login(username)
			else:
				login_code = stored_code

		return login_code
	
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
		
		self.game_version = self.get_game_version()

		# sleeping for a while to avoid having the two calls performed simultaneously
		initial_delay = random.randint(2, 10)
		util.tprint("[I] Sleeping for %s to avoid having the two calls too close together." % initial_delay)
		time.sleep(initial_delay)

		if username is not None:
			self.username = username
			self.access_token = self.get_login_code(username)
		else:
			self.access_token = self.get_access_token()
		
		util.tprint("[I] Ready to hunt")
