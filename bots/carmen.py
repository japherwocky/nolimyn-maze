triggers = ['\n\r',]

LOGIN = True
WANDER = False

import re, os

rsprompt = re.compile( r'<(-?[\d]{1,4})hp (-?[\d]{1,4})m (-?[\d]{1,4})mv (-|\+)>')
exittrig = re.compile(r"\[Exits: ([northeawsupd \(\)]*)\]")

class Bot:
	events = ['',]
	buffer = ''

	def __init__(self):
		self.read = self.login #login will swap itself out later 

#whatever data the mud has sent - lines are marked with \n\r :(
	def proc(self,str):
		import sys
		#print 'Processing from carmen...'
		sys.stdout.write( str )
		self.buffer += str
		#set self.read = whatever parsing func should take first shot
		return self.read()

	

	def readPrompt(self):
		match = rsprompt.search( self.buffer)
		event = ''
		while match:
			event = self.buffer[:match.start()]
			self.hps, self.mps, self.mvs, self.lag = match.groups()
			if exittrig.search( event):
				self.room = event.split('\r\n', 1)[0]
				if '\n\r' in self.room:
					self.room = self.room.split('\n\r', 1)[1].strip('\n')
				f = open('/tmp/roomwtf.log', 'a')
				f.write( 'Room: (%s)' % self.room)
				f.close()
				print 'ROOM IS (%s)' % self.room
				
			self.events.append( event)
			self.buffer = self.buffer[match.end():]
			match = rsprompt.search( self.buffer)

		return self.wander()

	def wander( self):
		from random import choice
		while len( self.events) > 0:
			foo = exittrig.search( self.events.pop() )
			#print foo, '%d in events'%len(self.events)
			if foo:
				exits = foo.groups()[0].split(' ')
				#avoid doors
				exit = choice( exits )
				if '(' in exit:
					while '(' in exit:
						exit = choice(exits)
					return exit
				else:
					return exit
		return ''

	def login(self ):
		str = self.buffer
		if 'traveller' in str:
			self.buffer = ''
			return 'Eeymore\n%s\n' % os.environ['CARMENPWORD']

		if '[Hit Return to continue]' in str:
			self.read = self.readPrompt
			self.LOGIN = False
			return '\n'

		if 'Reconnecting. Type replay to see missed tells' in str:
			self.read = self.readPrompt
			self.LOGIN = False
			return 'look'

"""
import re

stalledtrigs = [
	 re.compile(r"You are hungry."),
	 re.compile(r"You are thirsty."),
 	re.compile(r"Nah... You feel too relaxed..."),
 ]

guildtrigs = [
re.compile(r"I cannot allow you to pass."),
re.compile(r"The zealot guildguard growls and fiercely shakes his head at you"),
re.compile(r"slowly draws his sword, shaking his head silently"),
re.compile(r"The healer guildguard shakes his head silently."),
re.compile(r"guildguard says"),
re.compile(r"A rustle in a nearby bush alerts you to a ranger's angry eyes."),
re.compile(r"The Guardian Hunter growls and blocks the way inward."),
re.compile(r"The anti-paladin guildguard shoves you backward with a smirk."),
re.compile(r"The shapeshifter guildguard bares his still very human teeth at you."),
]

	
	for guildtrig in guildtrigs:
		foo = guildtrig.search(str)
		if foo:
			return 'look'

	#foo = stalledtrig.match(str)
	for stalltrig in stalledtrigs:
		foo = stalltrig.search(str)
		if foo:
			return 'stand\nlook'

"""

