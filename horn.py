#!/usr/bin/python

# Author: shade (Copyright C 2013)
#
# License: http://www.wtfpl.net/txt/copying/


import sys, getopt, getpass
from mh import MH

def usage():
	print ""
	print "USAGE: horn.py [params]"
	print "EXAMPLE: ./horn.py"
	print ""
	print "PARAMETERS: -m, -u, -h"
	print ""
	print "  -h, --help => Help - prints this text."
	print "  -m, --mode => Mode - can be tourney, normal (default), or keepalive."
	print "  -u, --username => Username for off-site play. If passed, a password will be required when run."
	print ""
	print "EXAMPLES:"
	print "  ./horn.py -m keepalive"
	print "  ./horn.py -m tourney -u dragan"
	print "  ./horn.py -u dragan -m keepalive"
	print "  ./horn.py -u dragan --mode tourney"
	print ""
	exit(1)

def main(argv):
	try:
		opts, args = getopt.getopt(argv, "hu:m:", ["help", "username=", "mode="])
	except getopt.GetoptError:
		usage()
		sys.exit(2)

	mode = None
	username = None
	password = None

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			exit(1)
		elif opt in ("-m", "--mode"):
			mode = arg
		elif opt in ("-u", "--username"):
			username = arg

	if mode is None:
		mode = "default"

	game = MH(mode, username)
	game.loop()


if __name__ == "__main__":
	main(sys.argv[1:])
