from collections import defaultdict
from itertools import chain
from sets import Set

import maze


asciimap = {
	-2:'*', #void
	-1:'%', #border
	0:'%',  #wall
	1:' ',  #fork
	2:' ',  #path
	3:'#',  #start
	4:'$',  #goal
	}

from room import Room, Solid, Void, Path, Goal, Start, Waypoint
terrainmap = {
	-2:Void, 
	-1:Solid,
	0:Solid,
	1:Path,
	2:Path, #correctpath? maybe could stop always checking for in solution
	3:Goal,
	4:Start,
	5:Waypoint,
}
	

class Board:
	"""
	Generates and maintains state of a maze / players
	"""

	def __init__(self, size, length=False):
		"""
		maze comes in like { 0:'.', 1:'%', 2:0, }
		TODO: maybe use proper ints for all room types
		TODO: use a tuple instead of a dict?!
		"""

		#make the maze; i think maze, solution are lists of rooms
		self.maze, self.solution, self.distances = maze.recursivebacktracker( size, length)
		while length and length > len(self.solution):
			self.maze, self.solution, self.distances = maze.recursivebacktracker( size, length)	

		#self.solution.reverse()
		self.D = size #square mazes only :)

		#cache what can be seen from each room
		#TODO: kind of weird/wasteful to do this for each Board()
		self.views = self.mkViewArray()

		#set up waypoints for instantiation
		for waypoint in [ self.solution[i] for i in pickwaypoints( len(self.solution))]:
			self.maze[waypoint] = 5 #see terrainmap

		#instantiate rooms
		self.maze = [ terrainmap[ self.maze[room]](Board=self) for room in self.maze]

		#mark distances from maze end
		for i in self.distances:
			self.maze[i].distance = self.distances[i]

		#mark distances from solution-path
		self.calcpathdistance()


		## set up HTML templates
		from genshi.template import TemplateLoader
		import os
		loader = TemplateLoader(
			os.path.join(os.path.dirname(__file__), 'templates'),
			#os.path.dirname(__file__),
			auto_reload=True
			)	
		self.tmpl = loader.load('map.html')

	@property
	def level(self):
		if hasattr(self, '_level'): return self._level
		self._level = self.Book.boards.index( self)
		#i think you can just do "self.level = foo" and wipe out the property
		return self._level

	def spawn(self, Body, Room=None):
		if not Room:
			Room = self.maze[ self.solution[0]]

		if not Room.enter( Body): return False

		#set a start time to calc scores
		if Room == self.maze[ self.solution[0]]:
			#ehhh, so 
			Body.Player.progress[ self.level] = 0 
			Body.Player.save()

		Body.Room = Room
		#then push to anyone in view
		self.pushrender( Room)

		return True

	def remove(self, Body):
		if not Body.Room.exit( Body): return False
		self.pushrender( Body.Room)	

	def neighbor(self, Body, direction):
		"""Get a Body in an adjoining room"""

		#figure out which room to look in
		l = self.maze.index( Body.Room)

		if direction == 'north':	l-=self.D
		elif direction == 'east':	l += 1
		elif direction ==	'south':	l += self.D
		elif direction ==	'west':	l -= 1

		if self.maze[l].bodies:
			#in theory, rooms should only have one body at a time
			return self.maze[l].bodies[0]

		return False


	def move(self, Body, direction):
		if not Body.Room.exit( Body): return False

		l = self.maze.index( Body.Room)
			
		if direction == 'north':	l -= self.D
		elif direction == 'east':  l += 1
		elif direction == 'south':	l += self.D
		elif direction == 'west':	l -= 1

		if not self.maze[l].enter( Body):
			Body.Room.enter( Body)
			return False

		Oldroom = Body.Room
		Body.Room = self.maze[l]
		self.pushrender( self.maze[l], Oldroom)
		return True


	def pushrender(self, Room, Oldroom=False):
		"""push a render to anyone within seeing distance of a Room;
		the tricky part is, when moving out of someone's range, so we
		need to first grab everyone within initial range
		"""

		#set makes sure we only get one copy of each body
		bodyset = Set()
		if Oldroom:
			for room in self.viewlist( Oldroom):
				for body in self.maze[room].bodies:
					bodyset.add(body) 

		for room in self.viewlist( Room):
			for body in self.maze[room].bodies:
				bodyset.add(body)

		for body in bodyset:
			body.see()

	def render(self, Body):
		return self.renderViewHtml( Body)

	
	def renderViewAscii(self, body):
		"""
		Return the portion of the map that the player should see
		"""
		view = self.views[ self.maze.index( body.Room)]
		return '\n'.join( [' '.join( [str(self.maze[i]) for i in row]) for row in view])

	def renderViewHtml(self, body):
		"""
		Generate an HTML table equiv. of Ascii.
		"""

		if body.Room not in self.maze:
			import pdb;pdb.set_trace()

		view = self.views[ self.maze.index( body.Room)]

		m = {}
		for room in chain( *view):
			if room >= 0: #multiple voids break it
				m[room] = str( self.maze[room])

		#set all the voids to emptiness
		m[-1] = ' '
		#m[-1] = asciimap[ -2] # er.. what? sets -1 to void.. necessary?
	
		#pump through map.html
		tmpl= self.tmpl.generate( maze=m, view=view, user=body, area=False)
		return '!@#'+tmpl.render('html', doctype='html')

	def renderMapAscii(self):
		"""
		Render the whole dang thing!
		"""
		return maze.render( self.maze, self.D)

	def viewlist(self, Room):
		""" util to return all visible rooms as a list """
		chainee = self.views[ self.maze.index( Room)]
		foo2 = list( chain( *chainee))
		return foo2


	def calcpathdistance(self):
		"""
		call to iterate over the rooms and measure their
		distance from the path
		"""
		#so.. walk the path and flag all the rooms one step off

		parsed = Set()
		parsing = Set( self.solution)
		d = 0
		while len( parsing):
			d += 1
			parsing = parsing.difference( parsed)
			#print 'Parsing depth %d: %s' % (d, parsing)
			for i in list( parsing):
				room = self.maze[i]
				for neighbor in room.exits.values():
					if not neighbor in self.solution and not neighbor in parsed:
						parsing.add( neighbor) 
						self.maze[neighbor].pathdist = d
				parsed.add(i)

	def mkViewArray(self, vis=3 ):
		"""
		instead of doing edge checks every time, let's store a matrix of
		{ location:(visiblecells,)}

		e.g., from the room you're rendering, this points at an array of pointers,
		of the rooms visible

		"pointers" are integers, for an ordered list of rooms

		vis is how far (orthogonally) a player can "see";  a vis of 2 makes
		a 5x5 square
		"""
		D = self.D
		void = -1
		#top, right, bottom, left = maze.edges( self.D)
		#self.edges = top+right+bottom+left 
		master = [] #tuple it later

		def mkneighborhood( point):
			#up = point - (D*vis)
			#left = point - vis
			alpha = point - vis - (D*vis)
			return [[(alpha+col) + (row*D) for col in range(vis*2+1)] for row in range(vis*2+1)]

		"""
		Loop is like.. generate a 12x12 "view" for every room, then for
		each of the edges, trim out the wrong rooms
		"""


		#lookout, here comes some math :)
		def trimleft( array, scale):
			return [ scale*[void,] + row[scale:] for row in array]
		def trimright( array, scale):
			l = len(array[0])
			return [ row[:l-scale] + scale*[void,] for row in array]

		nullrow = [void for i in range(vis*2+1)]
		def trimtop( array, scale):
			return [nullrow for i in range(scale)] + array[scale:]
		def trimbottom( array, scale):
			l = len(array[0])
			return array[:l-scale] + [nullrow for i in range(scale)]


		for row in range( D):
			#top condition
			if row-vis < 0:
				for col in range( D):
					C = mkneighborhood( col+ (row*D))
					if col - vis < 0:
						C = trimleft(C, vis-col)
					elif col + vis >= D:
						C = trimright(C, col+vis-D+1)
					master.append( trimtop( C, vis-row))

			#bottom condition
			elif row+vis >= D:
				for col in range( D):
					C = mkneighborhood( col+ (row*D))
					if col - vis < 0: C = trimleft(C, vis-col)
					elif col + vis >= D: C = trimright(C, col+vis-D+1)
					master.append( trimbottom( C, (row+vis)-D+1 ))
				
			else:
				for col in range( D):
					C = mkneighborhood( col+ (row*D))
					if col - vis < 0: C = trimleft(C, vis-col)
					elif col + vis >= D: C = trimright(C, col+vis-D+1)
					master.append(C)

		return tuple( master)

def stats():
	#see sample output below
	stats = []
	for i in range(5,20):
		sample = [len(Board(i).solution) for j in range(25)]
		stats.append( (i,min(sample), max(sample), sum(sample)/len(sample))	)

	for stat in stats:
		print 'Lvl:%d Min:%d Max:%d Avg:%d' % stat

lenchart = [0,0,1,2,3,4,5,10,15,20,25,30,37,43,50,58,67,75,86,94,104,115,125]

def calcdimension( length):
	"""Pick a board dimension based on the desired solution length"""
	for i in range( len(lenchart)):
		if lenchart[i-1] <= length and length < lenchart[i]:
			return i-1

def pickwaypoints( length):
	i = length
	while i > 1:
		i = int( i * .61)
		yield i

"""
Lvl:5 Min:3 Max:7 Avg:5
Lvl:6 Min:5 Max:11 Avg:9
Lvl:7 Min:11 Max:17 Avg:14
Lvl:8 Min:11 Max:23 Avg:19
Lvl:9 Min:18 Max:31 Avg:23
Lvl:10 Min:23 Max:38 Avg:29
Lvl:11 Min:26 Max:43 Avg:35
Lvl:12 Min:34 Max:53 Avg:45
Lvl:13 Min:37 Max:58 Avg:47
Lvl:14 Min:44 Max:69 Avg:58
Lvl:15 Min:49 Max:82 Avg:66
Lvl:16 Min:66 Max:99 Avg:76
Lvl:17 Min:67 Max:106 Avg:87
Lvl:18 Min:70 Max:117 Avg:91
Lvl:19 Min:89 Max:126 Avg:104
"""

