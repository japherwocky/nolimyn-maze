"""
Script to seed database of cards


client sends: inventory slot, target square

server looks up: card from inventory slot, global coords from tile

calls Card with Playerobj (we already looked this up to look up inventory) and target slot

return rendering instructions as {'login': ['instructions']}



each player needs.. a full inventory, and equipped slots

each card needs:

name:
uniqname:
image (100x100):
#description (txt):
code( python):

"""

"""
TO MAKE A CARD:

"""

from M import M, db
from board import redraw, rendercubes, whocanseecube
import commands
from logging import info, warning, error
from random import choice

import tornado

class Color:
    def __init__(self, color):
        self.color = color

 
    def __call__(self, Player, target, *args, **kwargs):
        x,y,z = target
        targetcube = M[db].cubes.find_one( {'x':x, 'y':y, 'z':z}) or M[db].cubes.find_one( {'x':x, 'y':y, 'z':z-1})

        if not targetcube: return {}

        targetcube['color'] = self.color

        M[db].cubes.save( targetcube)
        renders = {}
        for player in whocanseecube( x,y,z):
            #super lazy, pushing a full screen refresh
            renders[ player['login']] = rendercubes( player['x'], player['y'], player['z'])
        return renders


def Create( Player, target, *args, **kwargs):
    x,y,z = target

    # grab any cubes we might need to calc this
    q = {   'x': {'$gte': x-1, '$lte': x+1},
            'y': {'$gte': y-1, '$lte': y+1},
            'z': {'$gte': z-2, '$lte': z},
            }
    targetcubes = M[db].cubes.find( q)

    #translate to local coordinates, build xyz indexed dict:
    localcubes = {}
    for cube in targetcubes:
        #cube = localizeobj( cube, x,y,z)
        localcubes[ '%d%d%d' %(cube['x'], cube['y'], cube['z'])] = cube

    if '%d%d%d'%(x,y,z) in localcubes:
        #if wall exists, no possible moves
        return {}

    elif '%d%d%d'%(x,y,z-1) in localcubes:
        #if floor exists, build cube on top of it
        M[db].cubes.insert( {'x':x, 'y':y, 'z':z, 'color':'123456'}, safe=True)

        renders = {}
        for player in whocanseecube( x,y,z):
            #super lazy, pushing a full screen refresh
            renders[ player['login']] = rendercubes( player['x'], player['y'], player['z'])
        return renders

    else:
        #try to build floor tile, but see if gravity supports it first
        neighbors = [
                '%d%d%d'%(x-1,y,z-1),
                '%d%d%d'%(x+1,y,z-1),
                '%d%d%d'%(x,y-1,z-1),
                '%d%d%d'%(x,y+1,z-1),
                '%d%d%d'%(x,y,z-2),
                '%d%d%d'%(x,y,z+1),
            ]

        legal = False
        for n in neighbors:
            if n in localcubes:
                legal=True
                break

        if not legal: 
            return {}

        M[db].cubes.insert( {'x':x, 'y':y, 'z':z-1, 'color':'123456'}, safe=True)

        renders = {}
        for player in whocanseecube( x,y,z-1):
            #super lazy, pushing a full screen refresh
            renders[ player['login']] = rendercubes( player['x'], player['y'], player['z'])
        return renders

def Destroy( Player, target, *args, **kwargs):
    x,y,z = target

    # grab any cubes we might need to calc this
    q = {   'x': {'$gte': x-1, '$lte': x+1},
            'y': {'$gte': y-1, '$lte': y+1},
            'z': {'$gte': z-2, '$lte': z},
            }
    targetcubes = M[db].cubes.find( q)

    #translate to local coordinates, build xyz indexed dict:
    localcubes = {}
    for cube in targetcubes:
        #cube = localizeobj( cube, x,y,z)
        localcubes[ '%d%d%d' %(cube['x'], cube['y'], cube['z'])] = cube

    if '%d%d%d'%(x,y,z) in localcubes:
        #if wall exists, zap it
        M[db].cubes.remove( {'x':x, 'y':y, 'z':z}, safe=True)

    elif '%d%d%d'%(x,y,z-1) in localcubes:
        #if floor exists, zap it
        M[db].cubes.remove( {'x':x, 'y':y, 'z':z,}, safe=True)

    else: return {}

    renders = {}
    for player in whocanseecube( x,y,z):
        #super lazy, pushing a full screen refresh
        renders[ player['login']] = rendercubes( player['x'], player['y'], player['z'])
    return renders


def Teleport( Player, target, *args):
    #disappear from xyz,

    info( '%s attempts to teleport!'% Player['login'] )

    renders = {}
    for player in whocanseecube( Player['x'], Player['y'], Player['z'] ):
        #super lazy, pushing a full screen refresh to everyone in sight of player to/fro
        #really should just re-render the one cube player was standing on
        #really really should play a little poof out animation
        renders[ player['login']] = rendercubes( player['x'], player['y'], player['z'])

    #find a new coordinate
    i = 0
    while i < 35:
        i += 1
        cube = M[db].cubes.find()[choice( range( M[db].cubes.count()))] #random cube
        if M[db].cubes.find_one( {'x':cube['x'], 'y':cube['y'], 'z':cube['z']+1}):
            continue

        if M[db].players.find_one( {'x':cube['x'], 'y':cube['y'], 'z':cube['z']+1}):
            continue

        Player['x'] = cube['x']
        Player['y'] = cube['y']
        Player['z'] = cube['z']+1
        break

    #update db
    M[db].players.save( Player)

    #appear in new coordinate
    for player in whocanseecube( Player['x'], Player['y'], Player['z'] ):
        #super lazy, pushing a full screen refresh to everyone in sight of player to/fro
        renders[ player['login']] = rendercubes( player['x'], player['y'], player['z'])

    return renders
      
import random
def Draw( Player, target, *args, **kwargs):

    #replace draw card with a random one
    for slot in Player['equipped']:
        if Player['equipped'][slot] == 'draw':
            Player['equipped'][slot] = random.choice( Cards.keys())
            M[db].players.save( Player, safe=True)
            return {Player['login']: renderinventory( Player['login'])} #lazy, renderinv hits db.
         
    return {} 

def Leap( Player, target, *args, **kwargs):
    """ Dunno.. it's more of a giant ass sprint really """

    #calculate direction .. east for now
    deltax = target[0] - Player['x']
    deltay = target[1] - Player['y']
    print deltax,deltay

    a = deltax if deltax > deltay else deltay
    b = deltay if deltax > deltay else deltax

    while a > 0 or b > 0:
        a -=1
        b -=1
        #print a,b

    return {}
    #import pdb;pdb.set_trace()
    #take direction / distance and translate to nsew

    dirs = ['east','east','east','east','east']

    t = 1
    for d in dirs:
        tornado.ioloop.DelayedCallback( lambda: commands.parse( 'east', Player['login']), t ).start()
        t += 100

    return {}

from board import damage
def Pewpew( Player, target, *args):
    victim = M[db].players.find_one( {'x':target[0],'y':target[1],'z':target[2]})

    renders = damage( Player, 1, target[0],target[1],target[2]) 
    return renders

 
from collections import defaultdict
def Stair( Player, target, up=True, *args, **kwargs):   
    renders = defaultdict( lambda: [])

    #calc top and bottom squares:
    if up:
        bottom = target
        top = ( target[0], target[1], target[2]+1 )

    else:
        top = target
        bottom = ( target[0], target[1], target[2]-1 )

    #find/make cubes:

    botcube = M[db].cubes.find_one( {'x':bottom[0], 'y':bottom[1], 'z':bottom[2]} )
    if not botcube:
        botrenders = Create( Player, bottom)
        for player in botrenders:
            renders[player] += botrenders[player]
        botcube = M[db].cubes.find_one( {'x':bottom[0], 'y':bottom[1], 'z':bottom[2]} )

    topcube = M[db].cubes.find_one( {'x':top[0], 'y':top[1], 'z':top[2]} )
    if not topcube:
        toprenders = Create( Player, top)
        for player in toprenders:
            renders[player] += toprenders[player]
        topcube = M[db].cubes.find_one( {'x':top[0], 'y':top[1], 'z':top[2]} )


    if not topcube or not botcube:
        #gravity logic in Create dropped the stair one in the Z direction, probs

        #TODO: making too many queries for this card :(
        botcube = M[db].cubes.find_one( {'x':bottom[0], 'y':bottom[1], 'z':bottom[2]-1} )
        topcube = M[db].cubes.find_one( {'x':top[0], 'y':top[1], 'z':top[2]-1} )

    topcube['stair'] = 'down'
    botcube['stair'] = 'up' #boolean really, but whatever

    M[db].cubes.save( topcube)
    M[db].cubes.save( botcube)

    anchorcube = M[db].cubes.find_one( {'x':botcube['x'], 'y':botcube['y'], 'z':botcube['z']-1})
    if not anchorcube:
        bottom = (botcube['x'], botcube['y'], botcube['z']-1)
        print 'Making ', bottom
        botrenders = Create( Player, bottom)
        for player in botrenders:
            renders[player] += botrenders[player]
        

    return renders

def UpStair( Player, target, *args, **kwargs):
    renders = Stair( Player, target, True)

    if not renders: return {}

    return dict( renders)

Cards = {
    'whiteout':     Color( 'FFFFFF'),
    #'blueprint':    Color( '123456'),
    'create':       Create,
    #'destroy':      Destroy,
    #'draw':         Draw,
    #'leap':         Leap,
    'upstair':      UpStair,
    'teleport':     Teleport,
    'pewpew':       Pewpew,
    }
