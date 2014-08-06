"""
Called from stacklessmud.py, connections are made into Player()s.
"""

import string,stackless,logging,traceback,os
from cmds import galias,clist
from combat import Body
from prompt import Prompt

class Player:
	def __init__(self,conn,world):
		#so, the Connection class = self.connection
		#handles the networking stuff.  echoes go here?
		self.connection = conn

		#assign an id.. this should probably work differently.
		#this is the PLAYER name, until a login.
		self.id = str( id(self) )
		self.name = 'Guest%s' % (self.id) 
		
		self.body = Body(self)
	
		self.world = world.addPlayer(self)
		self.area = world.areas['!login'].addPlayer(self)
		self.room = self.area.rooms['login'].addPlayer(self)


		#set the prompt and commands..
		self.Prompt = Prompt(self)

		#so, players can lose/gain commands on the fly!
		self.commands = clist
		self.parseCommand('look')
		
		stackless.tasklet(self.Run)()

	#	WRITE FUNCTIONS

	#a line, with a carriage return
	def Push(self, msg):
		self.Write(msg + '\n')

	#little hacky, but for backwards compat:
	"""
	def Prompt(self,prompt=False):
		if prompt:
			self.prompt = prompt
		self.Write(self.prompt)
	"""
	def Echo(self, msg):
		msg = '%s\n' % (msg)
		self.Write(msg)
		self.Prompt()

	def Write(self,msg):
		try:
			self.connection.Write(msg)
		except AttributeError:
			#trying to write to someone who isn't there :)
			self.doDisconnect()
			

        #mm.. this should go in the server file
	def Run(self):

		logging.info("Connected %d from %s", id(self), self.connection.clientAddress)

		try:
			data = self.connection.ReadLine()
			while self.parseCommand(data):
				data = self.connection.ReadLine()

			self.OnUserDisconnection()
		except RemoteDisconnectionError:
			self.OnRemoteDisconnection()
			self.connection = None
		except:
			traceback.print_exc()
		finally:
			if self.connection:
				self.connection.Disconnect()
				self.connection = None

	def doTick(self):
		#self.Echo('TICK')
		pass
		
	#pass room/area as strings
	def Move(self,room,area=''):
		try:
			if area:
				#move areas
				self.area.remPlayer(self)
				self.area = self.world.areas[area].addPlayer(self)
			#move rooms
			self.room.remPlayer(self)
			self.room = self.area.rooms[room].addPlayer(self)

			self.parseCommand( 'look' )
		except KeyError:
			logstr = 'moving %s to %s from room:%s in area:%s'
			if (type(room)!=type('')) or (type(area)!=type('')):
				print 'Try passing in a string, smartass'
            #TODO: maybe check if it's an area, find the name
				logstr %= (self.id,'non-string',self.room.id,self.area.id)
				logging.warning(logstr)
			else:
				logstr %= (self.id,'nowhere room',self.room.id,self.area.id)
			
			logging.error(logstr)
			
		except:
			print 'Error moving',self.id,'to',room,area

	def parseCommand(self,data):
		if not data:
			self.Prompt() 
			return True
		args = string.split( data )
		command = args[0]
		args = args[1:]

		# first! check if the command is in the local exits!!
		if command in self.room.exits:
			args = [self.room.exits[command].dir]
			command = 'walk'
		#so, check of the command is an alias for something.
		elif command in galias:
			a = string.split(galias[command])
			command = a[0]
			args = a[1:] + args

		if command == 'quit':
			if clist['quit'].doCommand(self, self.world, args): #echoes to the room, etc.
				self.doDisconnect()
				return False
			else: return True

		#like above, perhaps this becomes commands.list
		#though, self.commands is pretty hot, actually.

		#do we need to check from clist?
		#TODO: ONLY IF WE HAVE SEPERATE SKILL SETS
		if command in clist:
			if command not in self.commands:
				x = "You aren't allowed to %s!!" % (command)
				self.Echo(x)
			else:
				com = clist[command]
				com.doCommand( self,self.world, args )
		elif command in self.room.funcs:
			fn = self.room.funcs[command]
			fn.fn.doCommand(self,self.world,fn.params,args)
		else:
			x = "No such command - '%s'" % (command)
			self.Echo(x)

		return True


	def OnRemoteDisconnection(self):
		logging.info("Disconnected %d (remote)", id(self))
		self.doDisconnect()

	def OnUserDisconnection(self):
		logging.info("Disconnected %d (local)", id(self))
		self.doDisconnect()

	def doDisconnect(self):
		self.room.remPlayer(self)
		self.area.remPlayer(self)
		self.world.remPlayer(self)

		try:
			self.connection.Disconnect()
		except AttributeError:
			#means the socket is dead, just ignore it
			pass

		#TODO: write the playerfile

class RemoteDisconnectionError(StandardError):
    pass

#this gets imported into funcs
class createplayer:
	def doCommand(self,pl,world,params,args):
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

      #Check if it exists..  TODO: world.path_to_pfiles?
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
import world
def newPlayerArea(pl):
	pl.id = '~' + pl.name
	#so.. link these into the World or not.. do, for pl.Move()
	pl.homeArea = pl.world.areas[pl.id] = world.Area(pl.id,pl.name)
	pl.homeRoom = pl.world.areas[pl.id].rooms[pl.id] = world.Room(pl.id,pl.name)
	#rethink this.. homeRoom?  Or fill in a template.
	pl.homeRoom.exits['login']=world.Exit('login','login','!login')

	#remember: Move takes strings, not Rooms/Areas
	pl.Move(pl.id,pl.id)

#Write a Pfile!
def write(player):
   #look at saxutils & .escape() in particular
	pass

