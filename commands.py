from M import M, db, Players
from copy import copy
from logging import info, error
from random import shuffle

from board import localizeobj, redraw, whocanseecube, renderplayers, chatbox

"""
commands return a {} of []s of javascript commands to be run by the client,
indexed by the loginname
"""

def argify( text):
    """
    Mostly just a note that "Commands" are expecting args
    to be a list of words/strings, not real args
    """
    return text.split()


def Chat( login, args):
    renders = {} 
    for player in Players:
        renders[player] = ["""$('#inbox').append("<p>[%s] %s</p>");""" %( login, ' '.join( args )) , ]

    return renders



def Move( login, direction):
    Player = M[db].players.find_one( {'login':login})
    
    x,y,z = Player['x'], Player['y'], Player['z']

    deltax = 0
    deltay = 0
    deltaz = 0


    #hrm.. seems like the qs should actually be 3s and 4s?

    if direction == 'north': 
        deltay += 1

        q = {
            'x':{'$gt':x-4, '$lt':x+4},
            'y':{'$gt':y-4, '$lt':y+5},
            'z': z,
            }

      
    elif direction == 'south': 
        deltay -= 1

        q = {
            'x':{'$gt':x-4, '$lt':x+4},
            'y':{'$gt':y-5, '$lt':y+4},
            'z': z,
            }

    elif direction == 'east': 
        deltax += 1 

        q = {
            'x':{'$gt':x-4, '$lt':x+5},
            'y':{'$gt':y-4, '$lt':y+4},
            'z': z,
            }

    elif direction == 'west': 
        deltax -= 1

        q = {
            'x':{'$gt':x-4, '$lt':x+4},
            'y':{'$gt':y-4, '$lt':y+4},
            'z': z,
            }

    x += deltax
    y += deltay


    #check legality of move
    #player in the way
    if M[db].players.find_one({'x':x, 'y':y, 'z':z}):
        return {}

    #wall or stair in the way
    targetcube = M[db].cubes.find_one({'x':x, 'y':y, 'z':z})
    if targetcube:
        if not 'stair' in targetcube: return {}
        if targetcube['stair'] == 'up':
            z += 1
            q['z'] = {'$gte':z-1, '$lte':z}

        if targetcube['stair'] == 'down':
            z -= 1
            q['z'] = {'$gte':z, '$lte':z+1}

    #no floor to walk on
    else:
        floorcube = M[db].cubes.find_one({'x':x, 'y':y, 'z':z-1})
        if not floorcube:
            return {}

        

    #move player
    Player['x'] = x
    Player['y'] = y
    Player['z'] = z
    M[db].players.save( Player)

    #calc list of players to push to (before we localize coords)
    players = M[db].players.find( q)

    renders = {}

    for P in players:

        if P['login'] == Player['login']: continue

        sprite = copy( Player)
        sprite = localizeobj( sprite, P['x'], P['y'], P['z'] ) #localize to the players screen

        #make javascript rendering instructions
        render = [
            """ $('#%s').remove() """ % ( sprite['login']) ,         #remove player's sprite
            ]
        #if we didn't move up/down, load new sprite:
        if P['z'] == z:
            render.append( """$('#%d%d').children().remove()""" %(sprite['x'], sprite['y'])) #clear stair landing sprites
            render.append( 
                """ $('#%d%d').append( '<p id="%s" class="player">%s</p>')""" % \
                    (sprite['x'], sprite['y'], sprite['login'], sprite['login'][0] )
                )

        renders[ P['login']] = render

    foo = [""" $('#%s').remove() """ % ( Player['login']) ,]         #remove old sprite
    renders[ Player['login']] = foo + redraw( x,y,z) #lazy, redrawing all of player's screen

    #send player new coordinates
    renders[ Player['login']] += [ 
        '$("#x").html( "%d" )' % Player['x'],
        '$("#y").html( "%d" )' % Player['y'],
        '$("#z").html( "%d" )' % Player['z'],
        ]


    return renders


def North( login, *args): return Move( login, 'north')
def East( login, *args): return Move( login, 'east')
def South( login, *args): return Move( login, 'south')
def West( login, *args): return Move( login, 'west')

from board import globalize
from cards import Cards
def Play( login, args):
    if not len(args) == 2: return {}
    slot, localcoords = args

    Player = M[db].players.find_one({'login':login})
    if not slot in Player['equipped']: 
        warning( '%s playing unequipped cards?'%login)
        return {}
    tcoords = globalize( Player['x'], Player['y'], Player['z'], int(localcoords[0]), int(localcoords[1]))

    card = Player['equipped'][slot]
    info( '%s plays %s @ %s'%(login,card,tcoords) )  
    if not card in Cards: return {}
    return Cards[card](Player, tcoords)

from board import renderdeck
def Deck( login, *args):
    Player = M[db].users.find_one( {'login': login})
    return { login: renderdeck( login) }    


def Shuffle( login, *args):
    """ give a new set of cards """
    Player = M[db].players.find_one( {'login':login})
    cards = Cards.keys()
    shuffle(cards)

    for i in range(1,4):
        Player['equipped']['slot%d'%i] = cards[i-1]

    M[db].players.save( Player, safe=True)
    return { login: renderdeck( login) }    

from board import renderhealth
def Health( login, *args):
    js = renderhealth( login)
    info( js)
    return { login: js}

from mob import StalkBot
from tornado.ioloop import PeriodicCallback
def Spawn( login, *args):
    monster = StalkBot( login)

    renders = {}
    for player in whocanseecube( monster.x,monster.y,monster.z):
        renders[ player['login']] = renderplayers( player['x'],player['y'],player['z'] ) 

    return renders
        
    



Commands = {
    'move':     Move,
    'north':    North,
    'east':     East,
    'south':    South,
    'west':     West,
    'play':     Play,
    'deck':     Deck,
    'chat':     Chat,
    'shuffle':  Shuffle,
    'health':   Health,
    'spawn':    Spawn,
    }


def parse( cmd, login):
    #commands should return rendering directions indexed by player

    raw = cmd.split(' ',1)
    cmd = raw[0]
    if len(raw) > 1:
        args = raw[1].split(' ')
    else:
        args = None

    try:
        output = Commands[cmd]( login, args)
    except KeyError:
        output =  {login: ["""$('#inbox').append("<p>Sorry, you don't know how to %s!</p>");"""%cmd,]}
    except:
        raise

    #sometimes the user isn't in output?
    if login not in output: output[login] = []

    output[login].insert(0, """$('#inbox').append('<p class="usercmd">&gt; %s</p>');""" % cmd)


    for user in output:
        if not user in Players: continue
        if not Players[user]:
            Players[user] = output[user]
        else:
            try:
                Players[user] += output[user]
            except:
                Players[user]( output[user])

