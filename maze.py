
"""
Generates mazes

as a sorted list of solid/void "Rooms"
"""



import random, sys
from itertools import chain

"""
>>> sys.stdout.write(' '+ ' '.join([' '.join([ str(rand()) for i in range(X)])+'\n' for i in range(Y)]))
 1 0 1 1 0 0 0 1 1 1 0 1 0
 0 1 0 0 1 0 0 1 1 1 0 1 0
 0 1 0 0 1 0 1 1 0 1 1 1 0
 0 0 1 0 0 0 0 0 0 1 1 1 0
 1 1 0 1 0 0 1 0 1 1 1 1 0
 0 0 1 1 0 0 1 0 1 0 1 1 0
 0 0 0 1 0 1 0 0 1 1 0 0 0
 1 1 1 0 1 0 0 1 0 1 1 0 0
 0 0 1 0 1 0 1 1 0 0 0 1 0
 1 0 0 0 1 1 0 0 0 0 0 1 0
 1 0 1 0 0 1 0 0 1 0 1 1 0
 1 1 0 1 0 1 0 0 1 1 1 1 1
 1 1 0 0 1 1 0 0 1 0 1 1 1
"""

#square only, ok?

def canvas(size=13):
	cells = {}
	for i in range(size**2):
		cells[i] = 0

	return cells

def render(maze, size):
	#kind of interesting pattern but not what we're looking for :P
	#sys.stdout.write(' '+ ' '.join([' '.join([ str(canvas[r*c]) for r in range(size)])+'\n' for c in range(size)]))

	# for some reason, this fills in the top right corner?!
	#print (' '+ ' '.join([' '.join([ str(maze[ (r*size) + c]) for r in range(size)])+'\n' for c in range(size)]))

	out = ''
	for row in range(size):
		for col in range(size):
			index = (row*size)+col
			#sys.stdout.write(' %3d:%s'%( index, maze[index]))
			out+= ' '+ str( maze[ (row*size) + col])
		out += '\n'

	return out


def edges(size=13):
	"""
	Returns a [ [top], [right], [bottom], [left]],
	where the "borders" are lists of numbers representing
	indices in a sorted list of all rooms.
	"""


	#top row
	top = range(1,size-1) or 1
	bottom = range( (size*(size-1))+1, (size**2)-1)
	left = range( size, (size**2)-size, size)
	right = range( (size*2)-1, (size**2)-1, size)

	#return borders
	return [top, right, bottom, left]

def corners(size=13):
	tl = 0
	tr = size-1
	bl =  size * (size - 1 )
	br = (size * size) - 1

	return [tl, tr, bl, br]

def neighbors(cell, size):
	"""
	Only for non-edge cells!
	"""
	#cell = col+ row*size
	#row = cell / size #finally, a use for python's goofy integer division!
	#col = cell - ( row * size )

	right, left = (cell + 1), (cell - 1)
	bottom, top = (cell + size), (cell - size)

	return [top, right, bottom, left]


def recursivebacktracker(size, limit=False):
	import sets, random, time
	from itertools import chain

	starttime = time.time()

	maze = canvas( size)
	BORDER = -1
	WALL = 0
	DUG = 1
	PATH = 2
	START = 3
	GOAL = 4

	top, right, bottom, left = edges(size)
	edgeset = top+bottom+left+right
	cornerset = corners( size)

	#hm.. does this have to start on an edge?
	#start = random.choice( edgeset)
	start = random.choice( range(size**2))
	while start in edgeset or start in cornerset:
		start = random.choice( range(size**2))


	maze[start] = START 
	trail = [start,]

	#make sure second path goes into the maze
	"""
	this is optional too.. there's no reason we couldnt
	have a corridor along the edge of the map, though we
	would also have to tweak checkdiggable(), so it's
	probably more of a pita than it's worth
	"""
	here = neighbors( start, size)
	if start in top: here = here[2]
	elif start in right:	here = here[3]
	elif start in bottom: here = here[0]
	elif start in left: here = here[1]
	else: 
		nxt = random.choice(here)
		while nxt in edgeset or nxt in cornerset:
			nxt = random.choice(here)

		here = nxt

	trail.append(here)


	def checkdiggable( cell, here):
		if cell in edgeset or cell in deadends: return False
		for c in neighbors( cell, size):
			if maze[c] > 0 and ( c != here):
				return False
		return True

	frontier = (start, 0)
	backtracking = False
	distances = {}
	deadends= []
	while len(trail) > 1:
		here = trail.pop()
		maze[here] = '~'
		distances[here] = len(trail)
		#print render(maze, size)

		choices = neighbors( here, size)
		random.shuffle(choices)	#no shuffle makes interesting long hallways
		digging = True
		#grab the first choice we can
		while digging and (len(choices) > 0) :
			choice = choices.pop()

			if limit and len(trail)==limit:
				deadends.append(here) #dont dig here when backtracking
				break
				
			#print 'start',start, 'here', here,'trying', choice
			elif maze[choice] > 0: pass
			elif checkdiggable( choice, here):
				trail.append(here)
				trail.append(choice)
				digging = False

		if digging: 

			#if this is the longest distance, this route wins 
			if len(trail) > frontier[1]:
				frontier = (here, len(trail)) 
				path = [i for i in trail] + [here,]
		maze[here] = DUG

	for i in path: maze[i] = PATH
	for i in edgeset: maze[i] = -1
	maze[start] = GOAL
	maze[ frontier[0]] = START

	print 'Generated in %f seconds, Solution length: %d rooms' % ((time.time() - starttime), frontier[1])
	return maze, path, distances


def test(size=13):
	maze = canvas(size)

	t,r,b,l = edges(size)
	for cell in (t+r+b+l):
		maze[cell] = '%'
	render(maze, size)


if __name__=='__main__': 
	import sys
	#test( int(sys.argv[1]))
	print render( recursivebacktracker( int(sys.argv[1]))[0], int(sys.argv[1])) #pass a size!
	"""
	D = int( sys.argv[1])
	times = [ recursivebacktracker( D) for i in range(20)]
	print 'Max', max(times), ' Min', min(times)
	print 'Avg', sum(times) / float(len(times))
	"""




"""
/area/level/cell
"""
