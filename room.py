from copy import copy
import random


class Room:

	title = ""
	desc = '' #paragraph or so, maybe just an URL
	char = ' '
	distance = None
	pathdist = None

	def __init__(self, Board):
		self.bodies = []
		self.objs = []
		self.Board = Board
		self._exits = {}

		self.init()

	def init(self):
		pass

	@property
	def exits(self):
		if self._exits: return self._exits

		loc = self.Board.maze.index( self)
		D = self.Board.D

		paths = [('north',loc-D),
					('east',loc+1),
					('south',loc+D),
					('west',loc-1)]	
		
		for dir,l in paths:	
			if l in range( len(self.Board.maze)):
				if self.Board.maze[l].enter( False):
					self._exits[dir] = l

		return self._exits

	def render(self, debug=False):
		#check for bodies / objs
		if self.bodies:
			return self.bodies[-1].render()
		if self.objs:
			return self.objs[-1].render()
		if debug:
			if self.pathdist:
				return str( self.pathdist)
			if self.distance:
				return str( self.distance)
		return self.char

	def __str__(self): return self.render()

	def enter(self, Body=False):
		"""
		Called when a Body() tries to enter a room
		return True/False if the player succesfully moved

		override for traps!

		Allow a False body to indicate rooms are connected
		"""
		if self.bodies: return False
		if Body:
			if self.bodies: return False
			self.bodies.append( Body)
		return True

	def exit(self, Body):
		"""
		Called when a Body() tries to leave a room, see above
		"""
		self.bodies.remove( Body)
		return True

	def drop(self, Obj):
		"""
		Called when an obj wants to land
		"""
		#if Obj.cursed: return False
		self.objs.append( Obj)
		return True

	def get(self, Obj):
		"""
		Someone is trying to pick an obj up
		"""
		self.objs.remove( Obj)
		return True


class Solid(Room):
	title = "A solid Wall"
	char = '%'

	def drop(self, Obj): return False
	def enter(self, Body): 
		return False

class Void(Room):
	title = "An empty Void."
	desc = "It is pitch black. You are likely to be eaten by a grue."
	char = '-'
	def drop(self, Obj): return False
	def enter(self, Body): return False

class Path(Room):
	title = "A featureless Path"
	char = '.'
	pathdist = 0
	_desc = False

	@property
	def desc(self):
		if not self.pathdist and self.distance:
			return "You are in a maze of twisty passages, all alike."
		else:
			d = self.Board.solution[ self.distance]

			#overwrite this method with a cached desc
			self.desc = copy( self.Board.maze[d].desc)
			self.garble()

			return self.desc

		print 'garbled!'

	def garble(self):
		pool = self.desc.split()[1:][:-1]
		garblees = random.sample( pool, self.pathdist)
		for word in garblees:
			drow = [c for c in word]
			random.shuffle( drow)
			self.desc = self.desc.replace(word,''.join(drow), self.pathdist)


			


class Start(Room):
	title = "The Beginning"
	desc = "The Beginning of a new Chapter.  Good Luck!"
	char = '<'
	prevboard = False

class Waypoint( Path):
	title = "A Waypoint"
	char = '.'

	def enter( self, Body=False):
		if self.bodies: return False
		if Body:
			if self.bodies: return False
			self.bodies.append( Body)

		if isinstance( Body, PlayerBody):
			#what's "and"?
			if Body.Player.progress[ self.Board.level] < self.distance:
				pts = Body.Player.score( self.distance) 
				Body.Player.write( 'Waypoint passed, for %d total points.'%pts)

				Body.Player.progress[ self.Board.level] = self.distance
				Body.Player.save()

		return True

	def foo(self): pass

class Goal(Waypoint):
	title = "The end of a Maze"
	desc = "Hooray!  (Use '>' to go to the next level)"
	char = '>'
	nextboard = False


#down here to avoid circular imports in Waypoint
from body import PlayerBody
