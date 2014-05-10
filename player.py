"""
Represents a connection to the game; tracks account info,
parses incoming content and receives text to go to the
client
"""

import string,traceback,os,collections,time
from commands import Commands
from settings import dbconn as db

import pymongo
M = pymongo.Connection()

import cPickle

class Player:
	p = '<%(hp)s/%(mhp)shp %(mp)s/%(mmp)smp>'


	def __init__(self, user):
		self.buffer = collections.deque()
		self.waiter = False #callback waiting for lists/messages

		self.user = user

		self._load()

	def _load(self):

		user = M.noldb.players.find_one( {'login':self.user})

		#like { 'level':furthestroomint} ... doesn't support multi-book yet TODO
		self.progress = { 0:0}
		if 'progress' in user:
			for k in user['progress']:
				self.progress[ int(k)] = user['progress'][k]

		self.points = 0 if not 'points' in user else user['points']

		from body import PlayerBody
		self.Body = PlayerBody( self) # self.Body = Body.load( user)
		#todo, load the previous Body 
		if 'stats' in user: self.Body.stats = user['stats']

		self.Body.stats['xp'] = self.score()

		#set them into the right Board/Room from nolimyn.py

	def save(self):
		user = M.noldb.players.find_one( {'login':self.user})

		strprogress = {}
		for k in self.progress:
			strprogress[ str(k)] = self.progress[k]
		user['progress'] = strprogress
		del strprogress

		user['points'] = self.score()
		user['stats'] = self.Body.stats

		M.noldb.players.save( user)


	def __str__(self): return self.user

	@property
	def Board(self):
		return self.Body.Room.Board


	#to do snoops / multiple listeners, wrap these methods		
	def write( self, msg):
		"""expects things one line at a time"""
		self.buffer.append( msg)
		if self.waiter:
			self.read( self.waiter)
			self.waiter = False

	def read( self, callback):
		if self.buffer:
			callback( list(self.buffer))
			self.buffer.clear()
		else: self.waiter = callback


	def score( self, modifier=False):
		if modifier:
			self.points += modifier

		return self.points

	def prompt( self):
		return self.p % self.Body.stats


	def Parse( self, data):
		"""
		Commands are functions or classes that take Player, args as a string
		TODO:, strip javascript/html/xml out 
		"""
		self.buffer.append( '>'+data)
		if not data or data=='\n': #sent '' or somesuch
			self.write( self.prompt())
			#self.Prompt() 
			return

		if self.Body.lag > time.time():
			#self.write( str( time.time()))
			self.Body.lagq.append( data)
			return

		#first word is the command, anything else is args
		data = data.lstrip('>')
		if not data: data = '>'
		args = string.split( data )
		command = args[0]
		args = args[1:]


		try: 
			Commands[command](self, args)
		except KeyError:
			for cmd in Commands.keys():
				if cmd.startswith( command):
					Commands[cmd](self, args)
					break

			self.write( '%s ?' % command)


	def Quit(self):
		#self.Board.logout( self.serverid) #er.. wha? TODO
		del self
		

		






"""
routine to work through logins by hijacking our Prompt() 

cruft?
"""

#this gets imported into funcs
class createplayer:
	def doCommand(self,pl,board,params,args):
		self.save = pl.parseCommand,pl.Prompt.string
		self.pl = pl
		pl.parseCommand = self.nameParse
		pl.Prompt('Player Name:')

	def nameParse(self,data):
		if not data:
			self.Prompt()
			return True

		#TODO: scrub out punctuation!
		name = data.lower()

      #Check if it exists..  TODO: board.path_to_pfiles?
		if not os.path.exists('players/'+name+'.xml'):
			self.pl.room.remPlayer(self.pl)
			self.pl.name = self.pl.id = name
			self.pl.parseCommand = self.passParse
			self.pl.Prompt.string = 'Password:'
			self.pl.Prompt()
			return True

		else:
			self.pl.Echo('Sorry - that name is taken!')
			return True

	def nameExists(self,name):
		if os.path.exists('players/'+name+'.xml'): return True

	def passParse(self,data):
		if not data:
			self.pl.Prompt()
			return True

		if str(self.pl.Prompt) == 'Password:':
			self.pl.password = data
			self.pl.Prompt.string = 'Password (Again!):'
			self.pl.Prompt()
			return True

		elif '!' in str(self.pl.Prompt): #second pass
			if not data == self.pl.password:
				self.pl.Push("Hmm.. Those didn't match up.")
				self.pl.Prompt('Password:')
				return True

			else:
				self.pl.Push("Looks Good!  Let's get started!")
				#Set everything back to normal
				self.pl.parseCommand,self.pl.Prompt.string = self.save
				#make a generic area:
				#stackless.tasklet(newPlayerArea)(self.pl)
				newPlayerArea(self.pl)
				return True


	"""
	pl.homeArea = Area(id,name)
	pl.homeRoom = Room(id,name)
	pl.homeArea.rooms['password'] = yep
	"""

