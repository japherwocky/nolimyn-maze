import re, random
import sys
sys.path.append('contrib/')
from ircbot import SingleServerIRCBot


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

	if 'where' in Event.arguments():
		time.sleep(.5)
		ServerConnection.privmsg( Event.target(), self.body)

	#ServerConnection.privmsg(Event.target(), 'haaayyy, you said %s'%Event.arguments())

import feedparser
from random import randint
def propagandize():
	global last_propaganda
	d = feedparser.parse('http://feeds2.feedburner.com/fmylife')
	#i = randint( 0, len(d.entries))
	last_propaganda = d.entries[randint( 0, len(d.entries)-1)]
	return strip_tags( last_propaganda.description)

def strip_tags(value):
	"Return the given HTML with all tags stripped."
	return re.sub(r'<[^>]*?>', '', value)




def ircmain():
	bot = SingleServerIRCBot([('pearachute.net', 6668)], 'Eeymore', 'I AM A ROBOT')
	bot.connection.add_global_handler('invite', invited, -10)
	bot.connection.add_global_handler('pubmsg', chatparse, -10)
	#join/part/privmsg/pubmsg/privnotice/pubnotice
	bot.start()

import os, twitter
api = twitter.Api(username='eeymore', password=os.environ['EEYOREPWORD'])
fml = re.sub('FML', '', propagandize())

def chop(fml):
	return random.choice( [x for x in fml.split('.') if len(x)>13] )

fml = chop(fml)
while len( fml) > 140 or re.search('boyfriend', fml):
	print 'Too long, trying again.. (%d chars)'%len(fml)
	fml = chop( re.sub('FML', '', propagandize()))

status = api.PostUpdate( fml+'.')
print status
