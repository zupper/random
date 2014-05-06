#!/usr/bin/python

# Author: shade (Copyright C 2013)
#
# License: http://www.wtfpl.net/txt/copying/

import json

class MHServerResponse:
	status = None
	error = None
	
	# data --
	#	|-- have_bait
	#	|-- time_to_horn
	#	|-- catch -------
	#			|-- status
	#			|-- mouse
	#			|-- loot
	#			|-- gold
	#			|-- points
	#			|-- damage
	#	|-- player
	#			|-- TBD
	#
	# data will be raw response in case of errors
	
	data = None
	
	def __init__(self, response):
		response = json.loads(response.rstrip())
		
		if "error" in response:
		
			if response['error']['code'] == 100:
				self.status = "login"
				self.error = response['error']['message']
			elif response['error']['code'] == 400:
				self.status = "warn"
				self.error = response['error']['message']
			elif response['error']['code'] == 80:
				self.status = "update"
				self.error = "Need game version update"
		else:
			self.status = "ok"
		
		if "user" not in response:
			self.status = "error"
			self.error = "No user object present. Somethign is wrong"
			self.data = raw_response

		else:
			self.data = {
					"have_bait": response["user"]["trap"]["bait_id"] is not None,
					"time_to_horn": response["user"]["next_activeturn_seconds"],
					"catch": {
						"status": response["user"]["trap"]["last_activity"]["class_name"],
						"mouse": response["user"]["trap"]["last_activity"]["mouse"],
						"gold": response["user"]["trap"]["last_activity"]["gold"],
						"points": response["user"]["trap"]["last_activity"]["points"],
						"loot": response["user"]["trap"]["last_activity"]["loot"]
					}
				}
