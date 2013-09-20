#!/usr/bin/python

# Author: shade (Copyright C 2013)
#
# License: http://www.wtfpl.net/txt/copying/


class Settings:
	# delays min/max values below
	delay_min = 2
	delay_max = 60
	tourney_delay_min = 1
	tourney_delay_max = 20
	keepalive_delay_min = 2700
	keepalive_delay_max = 4200
	big_delay_min = 3600
	big_delay_max = 4800
	small_delay_min = 450
	small_delay_max = 1800

	# we keep track of big and small delays to avoid having
	# them consecutively or within a time frame
	min_horns_between_big_delay = 10
	min_horns_between_small_delay = 4
