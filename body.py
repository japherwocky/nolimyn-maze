from random import random, shuffle
from copy import copy
from time import time

import tornado.ioloop
class Body:
	ticklen = 10000 #in ms
	Player = False

	_atk = False
	_def = False
	_mag = False

	def __init__(self, name):
		self.name = name
		self.inv = [] #objs
		self.eq = {}  #gear

		self.ticker = tornado.ioloop.PeriodicCallback( lambda: self.tick(), self.ticklen)
		self.ticker.start()

		self._initstats()

	def _initstats(self):

		self.stats = {'hp':10, 'mp':10, 'xp':0, 'mhp':10,'mmp':10}
		#stances
		self._x = 1
		self._r = .6
		self.lagq = []
		self.lag = False

	def addlag(self):
		if self.lag:
			self.lag += .5
		else:
			self.lag = time() + 1

		tornado.ioloop.DelayedCallback( lambda: self.clear(), (self.lag - time()) *1000).start()

	def clear(self):
		if time() < self.lag:
			#sorry, todo: this is vulnerable to spam - spawn a callback for every cmd!
			tornado.ioloop.DelayedCallback( lambda: self.clear(), (self.lag - time()) *1000).start()
		else:
			if self.Player:
				self.Player.write( self.Player.prompt())
			self.lag = False
			lagq, self.lagq = self.lagq, []
			for cmd in lagq:
				self.Player.Parse( '>'+cmd)
		
		

	def render(self):
		return '@'

	def see(self):
		""" hook to see when other things come in range """
		pass

	def tick(self): 
		self.regen()

	def regen(self):
		if self.stats['hp'] < self.stats['mhp']: self.stats['hp']+=1
		if self.stats['mp'] < self.stats['mmp']: self.stats['mp']+=1

	def damage(self, dmg=1, attacker=False):
		self.stats['hp'] -= dmg
		if self.Player:
			self.Player.write('You are hit for %d damage!'%dmg)
		if self.stats['hp'] < 0:
			self.die( attacker)

	def die( self, attacker=False):
		self.ticker.stop()
		del self

	def stance( self, stance):
		if stance.startswith('a'):
			self._atk = True
			self._def = False
			self._mag = False
			if self.Player:
				self.Player.write( "You shift into an attacking stance.")

		elif stance.startswith('d'):
			self._atk = False
			self._def = True
			self._mag = False
			if self.Player:
				self.Player.write( "You shift into an defensive stance.")

		elif stance.startswith('r'):
			self._atk = False
			self._def = False
			self._mag = True
			if self.Player:
				self.Player.write( "You shift into a ranged stance.")

		else:
			self.Player.write( "Valid stances: Attack, Defense, or Ranged")

	def atk( self, Body):
		"""
		Body is whatever it's attacking!
		"""
		if Body._atk: 
			if self.Player: self.Player.write( 'You swing but are blocked.')
			return
		elif Body._mag:
			dmg = int( self._x*1.5)
			Body.damage( dmg)
			if self.Player: self.Player.write( 'You hit for %x damage!'%dmg)
			self._x = self._x / 2 or 1
		elif Body._def:
			r = random()
			if r < self._r:
				self._r = r+.2
				if self.Player: self.Player.write( 'You swing but it dodges!' )
			else:
				if self.Player: self.Player.write( 'You hit for %d damage!'%self._x)
				Body.damage( self._x, self)
				self._r = random()

			Body._x *= 2

			self._x = self._x / 3 or 1

		self._x += 1
		self.addlag()

	def ddef( self, Body):
		if Body._def: 
			if self.Player:
				self.Player.write( 'You circle your opponent.')
			return
		if Body._atk:
			if self.Player:
				self.Player.write( 'You hit for %d damage!'%self._x  )
			Body.damage( self._x)
			self._x *= 2

		if Body._mag:
			if self.Player:
				self.Player.write( 'Before you can attack, your opponent strikes you!')
			self.damage( Body._x / 2 or 1)
			self._r *=2


		self.addlag()

		#no lag

	def mag( self, Body):
		#like a bullet!

		def w( message):
			if self.Player:
				self.Player.write( message)

		w( 'You launch a projectile at something...')
		if Body._mag: 
			w( 'something knocks your projectile out of the air with their own!' )
			if Body.Player: Body.Player.write( 'You take aim and deflect an incoming projectile!')
			return

		r = random()

		if Body._def:
			r = random()
			if r < self._r:
				self._r = r
				w( 'but you narrowly miss!')
				if Body.Player:
					Body.Player.write( 'Something whizzes past you!')
			else:
				w( 'you hit for %d damage!'%self._x)
				if Body.Player:
					Body.Player.write( 'You are hit for %d damage!')
				Body.damage( self._x )		
				self._x = self._x /  2 or 1
				self._r += .2

		if Body._atk:
			w( 'Who dodges and returns an attack of their own!')
			if Body.Player:
				Body.Player.write( 'You counter the attack, and hit for %d damage!')
			self.damage( self._x)

		self.addlag()
		

from random import choice
from commands import Look
class PlayerBody( Body):
	_atk = True

	def __init__( self, Player):
		self.name = str( Player)
		self.Player = Player
		self.inv = []
		self.eq = {}

		self._initstats()

		self.ticker = tornado.ioloop.PeriodicCallback( lambda: self.tick(), self.ticklen)
		self.ticker.start()

	def see( self):
		Look( self.Player, False)

	def damage( self, dmg=1):
		self.Player.write( 'You take %d damage!' % dmg)
		self.stats['hp'] -= dmg
		self.Player.write( self.Player.prompt())
		if self.stats['hp']<0:
			self.die()

	def die( self, attacker=False):
		self.Player.write( 'You die!')
		self.stats['hp'] = int( .3 * self.stats['mhp'])
		self.Room.bodies.remove( self)
		self.Room.Board.pushrender( self.Room)
		self.Room.Board.spawn( self)


choices = ['north', 'south', 'east', 'west']
class Monster( Body):
	Room = False
	choices = copy(choices)

	_def = True #default

	def render( self): return 'X'

	def tick( self):
		if self.Room:

			if len( self.choices):
				dir = self.choices.pop()
			else:
				shuffle( choices)
				self.choices = copy( choices)
			
			self.Room.Board.move( self, choice(['north','east','south','west']))

		self.regen()

	def die( self, attacker=False):
		self.ticker.stop()
		if self.Room:
			self.Room.bodies.remove( self)
			self.Room.Board.pushrender( self.Room)
			self.Room = False

		if attacker and attacker.Player:
			attacker.Player.write( 'You killed the beast!')

