#!/usr/bin/python

# Author: shade (Copyright C 2013)
#
# License: http://www.wtfpl.net/txt/copying/


import sys
from mh import MH

if len(sys.argv) > 2:
	print ""
	print "USAGE: horn.py [tourney]"
	print "EXAMPLE: ./horn.py"
	print "EXAMPLE: ./horn.py tourney"
	print ""
	exit(1)

# params handling
if len(sys.argv) == 2:
	tourney_mode = sys.argv[1] == 'tourney'
else:
	tourney_mode = False

game = MH(tourney_mode)
game.loop()

