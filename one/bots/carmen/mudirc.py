from ircbot import SingleServerIRCBot

class foo: pass

body = foo()
body.room = 'I am not totally sure.'

last_propaganda = False

def invited(ServerConnection, Event): #both are irclib. instances
   """
   Event.arguments() == ['#hello']
   """
   for arg in Event.arguments(): #(there's only one though)
      ServerConnection.join( arg)

import time
def chatparse(ServerConnection, Event):
	#print dir(Event)
	#print Event.arguments()
	#print Event.source() # nick!~user@domain
	#print Event.target() # #channel

	if 'Carmen' in Event.arguments()[0]:
		print 'I hear someone calling!'
		if 'where' in Event.arguments()[0]:
			print 'Where am i?!', body.room
			ServerConnection.privmsg( Event.target(), body.room )

	#ServerConnection.privmsg(Event.target(), 'haaayyy, you said %s'%Event.arguments())


def go():
	spellingbot = SingleServerIRCBot([('pearachute.net', 6668)], 'Carmen', 'I AM A ROBOT')
	spellingbot.connection.add_global_handler('invite', invited, -10)
	spellingbot.connection.add_global_handler('pubmsg', chatparse, -10)
#join/part/privmsg/pubmsg/privnotice/pubnotice
	spellingbot.start()

