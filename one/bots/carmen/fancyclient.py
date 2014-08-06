import sys
from telnetlib import Telnet
from threading import Thread
host = 'pearachute.net'
port = 9998

t = Telnet()

"""
import sys
try:
	_foo = __import__(sys.argv[1],globals(),locals(),['proc','triggers'])
	proc = _foo.proc
	#triggers = _foo.triggers
except Exception, e:
	print e,'\n','print-only:'
	def proc( string): 
		sys.stdout.write( string)
	triggers = ['\r\n']
"""

"""
We have two basic threads - one to read/proc, and one to give
ourselves input capability.
"""

class Proc(Thread):
	def __init__(self, proc):
		Thread.__init__(self)
		self.proc = proc

	def run(self):
		global t
		while True:
			#print 'reading..'
			input = t.read_very_eager()
			write( self.proc( input))
			#write( self.proc( t.expect(['\r\n'])))

class Input(Thread):
	def run(self):
		while True:
			write( [sys.stdin.readline(),])

def write(msg):
	global t # ugh, why?
	for cmd in msg:
		if cmd: 
			t.write(cmd + '\n')

class IRC(Thread):
	def __init__(self, mudirc):
		Thread.__init__(self)
		self.mudirc = mudirc

	def run(self):

		#print 'running irc'
		self.mudirc.go()
		#mudirc.body = self.mudbot


def main():
	global t
	t.open(host,port)
	from mind import Bot
	mind = Bot()

	P = Proc( mind.proc)
	I = Input()

	import mudirc
	mudirc.body = mind #ugh my analogies are all fucked up .. this seems not threadsafe
	IRCthread = IRC( mudirc)


	GO = True
	P.start()
	I.start()
	#IRCthread.start()

import sys
if __name__=='__main__': 
	try:
		main()
	except:
		raise
		sys.exit(1)
