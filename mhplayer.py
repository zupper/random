#!/usr/bin/python

# Author: shade (Copyright C 2013)
#
# License: http://www.wtfpl.net/txt/copying/

from mh import MH
from mhserverresponse import MHServerResponse
from settings import Settings
import util, random, time

class MHPlayer:
	# state vars
	last_big_delay_horns_elapsed = 0;
	last_small_delay_horns_elapsed = 0;

	mode = None
	mh = None

	def print_catch(self, data):
		catch_string = "--- Mouse: %s, Gold: %d, Points: %d" % (data['catch']['mouse'], data['catch']['gold'], data['catch']['points'])
		if data['catch']['loot'] is not None and data['catch']['loot'] != "":
			catch_string = "%s, Loot: %s" % (catch_string, data['catch']['loot'])
		util.tprint(catch_string)

	def exit_error(self, reason):
		print "Don't know what happened, see the reason below:"
		print reason
		util.tprint("Exitting...")
	
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

	def play(self):
		while True:
			response = self.mh.hunt()
	
			if response.status == "error":
				error_delay = random.randint(50, 100)
				util.tprint("[E] Server replied wierdly (no JSON). Will retry once. Delay: %d. Raw response:" % error_delay)
				print(response.data)
				time.sleep(error_delay)
				
				response = self.mh.hunt()
				
			if response.status == "error":
				util.tprint("[E] No JSON in reply and already retried. Response:")
				print(raw_response)
				util.tprint("[E] Exiting...")
				exit(1)
			
			elif response.status == "login":
				util.tprint("[E] Session has expired. Reauthenticating...")
				self.access_token = self.mh.authenticate(True)		# refreshing the expired access token
				
				# have a small delay before trying to sound again
				next_delay = random.randint(1, 10)
				
			elif response.status == "update":
				# game has been updated, we have to get the new version
				next_delay = self.get_next_delay(response.data['time_to_horn'])
				
				new_version_delay = random.randint(50, 100)
				util.tprint("[E] Game has been updated, have to get new game version. Sleeping for %s to simulate restarting the app..." % new_version_delay)
				time.sleep(new_version_delay)
		
				self.mh.refresh_game_data()
				
				util.tprint("[I] Game version updated. Will sound in: %d" % next_delay)
		
			elif not response.data['have_bait']:
				# we have to make a decision on how to proceed
				player_data = self.mh.get_player_data()
				util.exit_error("Out of bait. Exiting to avoid detection...")
				exit(1)
	
			elif response.status == "warn":
				# user hunted recently, we have to wait more
				next_delay = self.get_next_delay(response.data['time_to_horn'])
				util.tprint("[E] Hunted recently. Status: %s. Time until horn: %d, will sound in: %d" % (response.data['catch']['status'], response.data['time_to_horn'], next_delay))
				
				if "catchsuccess" in response.data['catch']['status']:
					self.print_catch(response.data)
	
			elif response.status == "ok":
				# hunt should have been successful, set the delay for next time
				next_delay = self.get_next_delay(response.data['time_to_horn'])
				util.tprint("[I] Horn sounded. Status: %s. Will sound in: %d" % (response.data['catch']['status'], next_delay))
				
				if "catchsuccess" in response.data['catch']['status']:
					self.print_catch(response.data)
			else:
				# we don't know what happened, better stop altogether
				util.exit_error(response)
			
			# 30% chance for user to check their journal after hunting
			if random.randint(0, 1000) < 300:
				check_delay = random.randint(1, 5)
				time.sleep(check_delay)
				player_data = self.mh.get_player_data()

			time.sleep(next_delay)

	def __init__(self, mode, username):
		self.mh = MH(mode, username)
		self.mode = mode
