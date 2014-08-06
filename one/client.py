#! /bin/bash

from telnetlib import Telnet
host = 'pearachute.net'
port = 9998

t = Telnet()

import sys
try:
	_foo = __import__(sys.argv[1],globals(),locals(),['proc','triggers'])
	proc = _foo.proc
	triggers = _foo.triggers
except Exception, e:
	print e,'\n','print-only:'
	def proc(tuple): 
		sys.stdout.write( tuple[2])
	triggers = ['\r\n']

def main():
	t.open(host,port)

	while True:
		write( proc( t.expect(triggers)))


def write(msg):
	if msg: t.write(msg + '\n')

if __name__=='__main__': main()
