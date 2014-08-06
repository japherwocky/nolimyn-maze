from copy import copy

class Cell:
    def __init__(self, sides=4):
        self.sides = sides
        self.neighbors = [] # = ()
        self.token = False


"""
there is something interesting about expressing direction as
a distance (starting from 'up') along the circumference.  So,
c/#ofsides picks which neighbor
"""

#hrm.. sizes need to be single digit to work the indexing properly
class Board:
    index = {} # {'index':Cell, }
    def __init__(self, size=8, dimensions=2, wrap=False):
        self.dimensions = dimensions
        self.size = size
        self.cells = self.mkCells( ((size+1)**dimensions), 4 )#squares?
        self.index = self.mkIndex( size )
        self.tokens = []
        

    """
    So.. we need to construct one Cell for.. dimension^2 * size?

    well, for 2 dimensional anyhow, it's just size^2 .. so probably
    size^dimension
    """

    def mkCells(self, qty, shape):
        return [Cell(shape) for x in range(qty)]

    """
    OK.. then we'll place all of the cells onto the board.
    we'll go in each dimension simultaneously,
    first along the border so we can set up wrapping
    then with an algorithm that makes calculating neighbors convenient.
    """

    def mkIndex(self, size ):
        #link a cell to each possible index combination.
        index = {}
        d = range(self.dimensions)
        
        def mkcursor(val=0):
            return [val for x in d]
        
        #borders
        c = mkcursor()
        index[ cursor2int(c) ] = self.cells.pop()
        for i in d:
            for j in range(1, size):
                c = mkcursor()
                c[i] += j #;print c
                index[ cursor2int(c) ] = self.cells.pop()

        #diagonals
        for i in d:
            for j in range(1,size):
                c = mkcursor(j)
                index[ cursor2int(c) ] = self.cells.pop()

        #infill
        for i in d:
            for j in range(1, size):
                for k in range(1,j):
                    c = mkcursor(j)
                    c[i] = j-k #; print c
                    index[ cursor2int(c) ] = self.cells.pop()

        for cellnumber in index:
            index[cellnumber].index = cellnumber
         
        
        return index

    #eh.. so coordinate is a cursor?
    def neighborhood(self, coordinate, scope=int()):
        #move straight once in each direction
        #should return <= 2*dimension coordinates
        #(depending on wrapping)

        d = range(self.dimensions)
        neighbors = []
        
        def mkcursor(val=0):
            return [val for x in d]

        #straights:
        for i in d:
            for j in range(1, scope+1):
                for k in (-1,1):
                    c = copy(coordinate)
                    c[i] += j*k
                    neighbors.append(c)

        #neighbors.append( evendiags(scope // dimension))
        """
        so even diagonals get made at scope//dimension,
        go out and connect straight to the borders
       
        'odd' diagonals are like the other colored squre
        """

        def evendiags(coordinate, scope=int()):
            for i in d:
                for j in range(1,scope+1):
                    for k in (-1,1):
                        c = mkcursor(j)
                        #really this is matrix math at this point? we need
                        #to construct if (scope//dimension) < dimension:

                        #it's like.. lower dimensions and scopes don't even have
                        #diagonals.. so this should be before the for loop.

        return neighbors

def cursor2int(coordinate):

    out = ''
    for i in range( len(coordinate) ):
        out += str( coordinate[i] )

    return str(out)


def mkcursor(val=0, d=2):
    return [val for x in d]

class Token
    def __init__(self, board=False, cell=False, color=1):
        self.board = board if board else Board()
        self.cell = cell if cell else Cell()
        self.color = color
        cell.token = self
        board.tokens.append(self)

    def move(self, fromcell, tocell, do=True):
        """
        So we can do things like try all moves :/
        """
        class mvException(Exception): pass
        if tocell.token: raise mvException
        
        if do:
            fromcell.token = False
            tocell.token = self
        else:
            return True


            
"""
1d: (0),(1),(x)
2d: (0,0), (0,1), (1,0),  (0,x), (x,0)
3d: (0,0,0), (1,0,0) (0,1,0) (0,0,1),  
"""

"""
>>> for i in range(d):
	cursor = [0 for i in range(d)]
	for j in range(8):
		cursor[i]+=1; print cursor

		
[0, 0, 1]
[0, 0, 2]
[0, 0, 3]
[0, 0, 4]
[0, 0, 5]
[0, 0, 6]
[0, 0, 7]
[0, 0, 8]
[0, 0, 1]
[0, 0, 2]
[0, 0, 3]
[0, 0, 4]
[0, 0, 5]
[0, 0, 6]
[0, 0, 7]
[0, 0, 8]
[0, 0, 1]
[0, 0, 2]
[0, 0, 3]
[0, 0, 4]
[0, 0, 5]
[0, 0, 6]
[0, 0, 7]
[0, 0, 8]
>>> 
"""
#UNIT TESTS!!!
board = Board()
#board3d = Board(size=9, dimensions=3)

neighbors = board.neighborhood([0,0], 1)
