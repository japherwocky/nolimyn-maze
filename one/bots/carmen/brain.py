triggers = ['\n\r',]

LOGIN = True
WANDER = False

import re, os

rsprompt = re.compile( r'<(-?[\d]{1,4})hp (-?[\d]{1,4})m (-?[\d]{1,4})mv (-|\+)>')

cmds = re.compile( r'\x1b\[0;37m(.*)$', re.MULTILINE) #outgoing commands from tt++ logs
prompt = re.compile(  r'^([\w]*) <(-?[\d%]{1,4})hp (-?[\d%]{1,4})m (-?[\d%]{1,4})mv ([\d]{1,5})tnl .*>', re.MULTILINE) #stock cf prompt
exittrig = re.compile(r"\[Exits: ([northeawsupd \(\)]*)\]")
followtrig = re.compile(r'^You follow ([\w]*) ([\w]*)\.$', re.MULTILINE)


class Bot:

	"""
	Use like: Bot()
	Bot.read = lambda x: self.events.append( x.split())
	Bot.login()
	Bot.run()
	"""
	buffer = ''
	events = ['',]
	here = {} #state of current room

	ALIVE = True

	def __init__(self):
		self.read = self.login #login will swap itself out later 

#whatever data the mud has sent - lines are marked with \n\r :(
	def proc(self,str):
		import sys
		#sys.stdout.write( str )

		self.read( str)

		while self.ALIVE:
			self.read( str)
			yield self.analyze()

	### READ FUNCTIONS BREAK UP RAW TEXT FROM THE MUD INTO EVENTS

	def read(self):
		self.events.append( text.split())  #maybe do it by newline?

	def readlines(self):
		"""
		Read a body of text and set events to be full lines
		"""
		self.buffer += text
		lines = self.buffer.split('\n')
		#if we get a partial line, add it to the buffer and wait for the next batch
		#telnetlib could probably take care of this for us?
		self.buffer = lines.pop() if '\n' in lines[-1] else ''
		self.events.append( lines)


	def readPrompt(self):
		match = prompt.search( self.buffer)
		event = ''
		while match:
			event = self.buffer[:match.start()]
			self.roomtype, self.hps, self.mps, self.mvs, self.tnl = match.groups()
				
			self.events.append( event)
			self.buffer = self.buffer[match.end():]
			match = prompt.search( self.buffer)
		return self.wander()


	### ANALYSIS FUNCTIONS (MOODS?) READ EVENTS AND SEND COMMANDS TO THE BODY

	def analyze(self):
		event = self.events.pop()
		room = exittrig.search( event)
		if room:
			self.analyzeRoom( event)

	def analyzeRoom(self, event):
		cmd = cmds.search( event) #from tt++ logs
		fol = followtrig.search( event)
		if cmd:
			try:
				#ugh, sometimes we can spam commands too fast :\
				junk, cmd, event = cmds.split( event)
			except:
				import pdb;pdb.set_trace()
		elif fol:
			junk, leader, dir, event = followtrig.split( event)
			import pdb;pdb.set_trace()


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


if __name__=='__main__':
	B = Bot()
	B.read = B.readPrompt

	log = open('cf.log').read()

	B.proc(log)
