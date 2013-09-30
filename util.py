#!/usr/bin/python

# Author: shade (Copyright C 2013)
#
# License: http://www.wtfpl.net/txt/copying/

from datetime import datetime

def tprint (text):
	time = datetime.now().strftime("%H:%M:%S")
	print "[%s] %s" % (time, text)
	
def exit_error(reason):
	print "Don't know what happened, see the reason below:"
	print reason
	tprint("Exitting...")

	exit(1)
