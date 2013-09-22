#!/usr/bin/python

# Author: shade (Copyright C 2013)
#
# License: http://www.wtfpl.net/txt/copying/

class MHDecision:
	delay_time = None
	new_location = None
	buy_bait = None
	new_bait = None

class MHDecide:
	# state
	delay_time = None
	bait_type = None
	bait_count = None
	current_location = None
	location_baits = None

	decision = None

	def decide(self):
		# too stupid to decide just yet
		return MHDecision()

	def __init__(self, bait_type, bait_count, current_location, location_baits, game_mode):
		self.bait_type = bait_type
		self.bait_count = bait_count
		self.current_location = current_location
		self.location_baits = location_baits
		self.game_mode = game_mode

		self.decision = self.decide()
