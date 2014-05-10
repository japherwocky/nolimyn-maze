import array
from OpenGL.GL import *

from collections import defaultdict
from time import time

class Cube:
    _verts = False


    colors = array.array('f',
    [     0, 0, 0, .5,
        1, 0, 0, .5,
        1, 1, 0, .5,
        0, 1, 0, .5,
        0, 0, 1, .5,
        1, 0, 1, .5,
        1, 1, 1, .5,
        0, 1, 1, .5,
        ] ).tostring()

    Indices = array.array('B',
    [    0, 3, 2, 1,
        2, 3, 7, 6,
        0, 4, 7, 3,
        1, 2, 6, 5,
        4, 5, 6, 7,
        0, 1, 5, 4 ] ).tostring()



    def __init__(self, x,y,z):
        self.pos = dict( x=x, y=y, z=z)


    def vertices( self):
        if not self._verts:
            l = self.pos
            self._verts = array.array('f',
            [     -.5+l['x'],-.5+l['y'],.5+l['z'],
                -.5+l['x'],.5+l['y'],.5+l['z'],
                .5+l['x'],.5+l['y'],.5+l['z'],
                .5+l['x'],-.5+l['y'],.5+l['z'],

                -.5+l['x'],-.5+l['y'],-.5+l['z'],
                -.5+l['x'],.5+l['y'],-.5+l['z'],
                .5+l['x'],.5+l['y'],-.5+l['z'],
                .5+l['x'],-.5+l['y'],-.5+l['z'],
                ]).tostring()

        return self._verts

    def render( self):
        glColorPointer( 4, GL_FLOAT, 0, self.colors) #number of args, type, where to start
        glVertexPointer( 3, GL_FLOAT, 0, self.vertices() )
        glDrawElements( GL_QUADS, 24, GL_UNSIGNED_BYTE, self.Indices)


def gravityneighbors(x,y):
    xs = int(x), int(round(x+.5))
    ys = int(y), int(round(y+.5))
    neighbors = set()
    [[ neighbors.add((X,Y)) for X in xs] for Y in ys]
    return neighbors
             


class World:
    Tlast = time()
    def __init__(self, camera, cubes=None, radius=3):
        #center, ala 0,0,0 is radius, radius, radius
        """
        we store cubes then in a giant ordered list, going
        0,0,0 -> r,0,0 -> r,r,0 -> r,r,r
        """ 
        self.camera = camera

        self.cubes = defaultdict( lambda:False) #inanimate objs.
        self.objects = set() #animate objs.


    def tick(self):
        """
        So the idea is.. register forces with cubes and objects
        """
        for cube in self.objects:
            cube.move()
            if not cube.forces:
                self.objects.remove( cube)
        """
        or then, check if camera has moved and reorder the world? load edges
        """

    def gravity(self):
        t = time()
        Telapsed = t - self.Tlast
        for obj in self.objects:
            if obj.v:
                #update height
                obj.pos = ( obj.pos[0], obj.pos[1] + (obj.v*Telapsed), obj.pos[2])
                obj.v -= 10*Telapsed
                for ground in gravityneighbors( obj.pos[0],obj.pos[2]):
                    
                    if '%s,%s,%s'%(ground[0], int(round(obj.pos[1]))-1, ground[1]) in self.cubes:
                        obj.v = 0
                        obj.pos = (obj.pos[0], int(round(obj.pos[1]))+1, obj.pos[1])

        self.Tlast = t


    def spawnCube(self, x,y,z, cube):
        self.cubes[ '%s,%s,%s'%(x,y,z)] = cube

    def cull(self, Camera):
        #normalize sight vector, mebbe
        d = sum( [x**2 for x in Camera.sight])**.5
        sight= [10*x/d for x in Camera.sight]
        """
        The idea is to step outward along the line of sight from the camera pos
        and make a rough pass at the cubes we'll want to use
        """
        #print Camera.sight

        for c in self.cubes:
            yield self.cubes[c]
