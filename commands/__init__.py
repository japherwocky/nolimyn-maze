"""
Defines/maps to all commands.  To add a command to the game,
import it and add it to Commands below
"""

class command:
    name = 'Command'

    def __call__(self, Player, args):
        #work your magic
        pass

def Save( Player, args):
    Player._save()
    Player.write( 'OK')

def Score( Player, args):
    Player.write( '%d'%Player.score())
    Player.Prompt()

def Quit( Player, args):
    """"
    Check for fights, etc. at some point
    """
    Player.Quit()

import tornado.ioloop
def Fart( Player, args):
    """ delayed callback example"""
    tornado.ioloop.DelayedCallback( lambda: Player.write( '*toot*'), 2000, tornado.ioloop.IOLoop.instance() ).start()
    Player.write( 'You feel a pressure building inside ...')
    Player.Body.damage()

def Debug( Player, args):
    import pdb;pdb.set_trace()

def Look( Player, args=False):
    Player.write( Player.Board.renderViewHtml( Player.Body))

def Read( Player, args=False):
    Player.write( Player.Body.Room.desc)

def Prompt( Player, args=False):
    Player.write( Player.prompt())

def Move( Player, direction):
    if not Player.Board.move( Player.Body, direction):
        neighbor = Player.Board.neighbor( Player.Body, direction)
        if neighbor:
            B = Player.Body
            if B._atk:
                B.atk( neighbor)
            elif B._mag:
                B.mag( neighbor)
            elif B._def:
                B.ddef( neighbor)
            else:
                Player.write( 'That one cannot be harmed.')
        else:
            Player.write( 'You cannot go that way.')
    else:
        Look( Player)
        Read( Player)
        Prompt( Player)
        

def North( Player, args): Move( Player, 'north')
def East( Player, args): Move( Player, 'east')
def South( Player, args): Move( Player, 'south')
def West( Player, args): Move( Player, 'west')

from room import Goal
def Down( Player, args):
    if not isinstance(Player.Body.Room, Goal):
        Player.write( 'You cannot go that way.')
    elif not Player.Body.Room.nextboard:
        Player.write( 'Level %d? Why go further?'%Player.Body.Room.Board.level)
    else:
        Book = Player.Board.Book
        lvl = Book.boards.index( Player.Board)

        Book.boards[lvl].remove( Player.Body)
        Book.boards[lvl+1].spawn( Player.Body)
        Look( Player)
        Read( Player)

from room import Start
def Up( Player, args):
    if not isinstance(Player.Body.Room, Start):
        Player.write( 'You cannot go that way.')
    elif not Player.Body.Room.prevboard:
        Player.write( "But you're on level %d! Be brave!"%Player.Board.level)

    else:
        Book = Player.Board.Book
        lvl = Book.boards.index( Player.Board)

        Book.boards[lvl].remove( Player.Body)
        Book.boards[lvl-1].spawn( Player.Body, Book.boards[lvl-1].maze[ Book.boards[lvl-1].solution[-1]])
        Look( Player)
        Read( Player)
        

from random import choice
from itertools import chain
def Spawn( Player, args):
    from body import Monster    
    M = Monster( 'GRRAARR')
    Board = Player.Board

    #rooms = chain.from_iterable( Board.views[ Board.maze.index( Player.Body.Room)])
    rooms = Board.viewlist( Player.Body.Room)
    done = False
    while not done:
        done = Board.spawn( M, Board.maze[choice(rooms)] )
    

def Stance( Player, args):
    if not args:
        Player.write( 'Which stance do you want to use?')
        Player.body.stance( 'none')
        return

    Player.Body.stance( args[0])
    

Commands = {    
    'north'    :    North,
    'east'    :    East,
    'south'    :    South,
    'west'    :    West,
    'quit'    :     Quit,
    'fart'    :     Fart,
    'debug'    :    Debug, #drops a pdb.set_trace()
    'look'    :    Look,
    'spawn'    :    Spawn,
    's'        :    South, #hack to keep from spawning on south ;)
    '>'        :    Down,
    'down'    :    Down,
    '<'        :    Up,
    'up'        :    Up,
    'read'    :    Read,
    'score'    :    Score,
    'save'    :    Save,
    'stance'    :    Stance,
    }                





###  CRUFT


#are we catching this somewhere else?        
class cQuit(command):
    def doCommand(self,ch,world,args):
        #if ch.body.fighting: return False
        #else:
        lEcho('%s has left the game.' % ch.name, ch.room, ch)
        return True
        #ch.doDisconnect()

class cArea(command):
    def doCommand(self,ch,world,args):
        ch.Echo('Area: %s'%(ch.area.name))

class cLook(command):
    def __init__(self):
        self.name = 'look'
    def doCommand(self,ch,world, args):
        ch.Push( ch.room.name )
        #Push room description
        for i in ch.room.descrip.split('\n'):
            ch.Push( i )
        #Push objs
        #Push mobs
        for m in ch.room.mobs:
            m = '%s is here.' % ch.room.mobs[m].name
            ch.Push(m)
        #Push players
        for p in ch.room.players:
            p = ch.room.players[p]
            if not p.id == ch.id:
                p = '%s is here.' % (p.name)
                ch.Push(p)

        #Push Exits
        ch.parseCommand('exits')

class cWho(command):
    def __init__(self):
        self.name = 'who'

    def doCommand(self,ch,world,args):
        ch.Push('--- Who ---')
        for player in world.players:
            try:
                ch.Push(world.players[player].name)
            except:
                ch.Push(str(dir(player)))
        ch.Prompt()

class cPy(command):
    def doCommand(self,ch,world,args):
        from string import join
        
        try: exec(join(args))
        except: traceback.print_exc()
        ch.Push('.')
        ch.Prompt()

class cExits(command):
    def __init__(self):
        self.name = 'exits'
    def doCommand(self,ch,world,args):
        Pushexits = []
        for exit in ch.room.exits:
            ex = ch.room.exits[exit]
            if not (('hidden' in ex.flags) or ('secret' in ex.flags)):
                Pushexits.append(ex.dir)
        #TODO, check if it's not hidden from ch

#        ch.Echo('%s[Exits: %s]' % (TERMINATOR,string.join(Pushexits)) )
        ch.Echo('[Exits: %s]' % (string.join(Pushexits)) )

#pass this loop the string to echo to the room, but not to ch
#use ch.Echo(string) for the character
def lEcho(string,room,ch=''):
    from copy import copy
    if not ch:
        class foo:pass
        ch = foo()
        ch.id = 'foo'

    victims = copy(room.players) #like locking the data?
    """
    Funny bug where room.players would change size during this loop
    """
    for victim in victims:
        v = room.players[victim]
        if v.id != ch.id:
            v.Echo(string)

class cWalk(command):
    def __init__(self):
        self.name = 'walk'
    def doCommand(self,ch,world,args):
        d = args[0]
        
        if d in ch.room.exits:
            ex = ch.room.exits[d]
            #Echo if anyone else is in the room
            if len(ch.room.players) > 1:
                #so.. I made an excho flag to keep people from snooping logins?
                if 'excho' in ex.flags:
                    x = '%s leaves.' %(ch.name)
                else:
                    x = '%s leaves to the %s.'%(ch.name,d)
                lEcho(x,ch.room,ch)
                        
            #check if we're leaving the area
            if ex.area:
                ch.Move(ex.to,ex.area)
            else:
                ch.Move(ex.to)
            #Echo to whoever's in the destination room
            if len(ch.room.players) > 1:
                x = '%s has arrived.'%(ch.name)
                lEcho(x,ch.room,ch)
        else:
            ch.Echo("You can't go that way.")

class cSay(command):
    def __init__(self):
        self.name = 'say'
    def doCommand(self,ch,world,args):
        speech = string.join(args)

        if len(ch.room.players) > 1:
            x = '%s says, "%s"' % (ch.name,speech)
            lEcho(x,ch.room,ch)
        x = 'You say, "%s"' % (speech)
        ch.Echo(x)

class cTime(command):
    def doCommand(self,ch,world,args):
        t = str(world.Chronos.now)
        ch.Echo(t)

#Example of a timed command - toot toot.
class cFart(command):
    def doCommand(self,ch,world,args):
        ch.Echo('You let slip a little toot!')
        stackless.tasklet(self.spawnCommand)(ch,world,args)
        stackless.schedule()

    def spawnCommand(self,ch,world,args):
        room = ch.room
        world.Chronos.sleep(4)
        lEcho('pffffffffffffffffft.',room)

#import combat
class cFight(command):
    def doCommand(self,ch,world,args):
        if len(args) < 1: return ch.Echo('Who do you want to fight?')
        def fight(victim):
            stackless.tasklet(combat.NeoFight)(ch.body, victim)

        if (args[0] in ch.room.players):
            fight(ch.room.players[args[0]].body)
        elif (args[0] in ch.room.mobs):
            fight(ch.room.mobs[args[0]].body)
        else:
            return ch.Echo("They aren't here!")

            
class atks(command):
    def updateprompt(self,ch):
        ch.prompt = '<%s %s>'%(ch.body.atkq,ch.body.atk)
        
class cAtk(atks):
    def doCommand(self,ch,world,args):
        ch.body.setatk('atk')
        self.updateprompt(ch)
        ch.Echo('atk added to the queue.')
class cDef(atks):
    def doCommand(self,ch,world,args):
        ch.body.setatk('def')
        self.updateprompt(ch)
        ch.Echo('def added to the queue.')
class cMag(atks):
    def doCommand(self,ch,world,args):
        ch.body.setatk('mag hp')
        self.updateprompt(ch)
        ch.Echo('mag hp added to the queue.')

import random
class cFlee(command):
    def doCommand(self,ch,world,args):
        while len(ch.body.fights) > 0:
            ch.body.fights.pop().fighting=False
        ch.Push("You attempt to flee!")
        #eh... got to check to not flee into hidden exits
        ch.parseCommand( random.choice(ch.room.exits.keys()) ) #rm.. maybe a doCommand would work too.

class cScore(command):
    template = """--- SCORE ---\r\n
$name\n
$$ $wealth\n
Level $lvl ($xp xp)\n
$ap Allocation Points\n
${hp}/${maxhp}hp ${mp}/${maxmp}mp ${mv}/${maxmv}mv\n
${dex}/${maxdex}DEX ${str}/${maxstr}STR ${int}/${maxint}INT ${wis}/${maxwis}WIS\n
------"""

    def doCommand(self,ch,world,args):
        from string import Template
        s = Template(self.template)
        ch.Echo( s.safe_substitute(ch.body.stats))
        #ch.Prompt()
        """
        ch.Push('--- SCORE ---')    
        for stat in ch.body.stats:
            ch.Push('%s: %s'%(stat,ch.body.stats[stat]))
        ch.Prompt()
        """

class cSpawn(command):
    def doCommand(self,ch,world,args):
        from monsters import Monster #in the method to avoid circular import problem
        #world, area, room  = world, ch.area, ch.room
        stackless.tasklet(Monster)(world,ch.area.id,ch.room.id)
        stackless.schedule()
        ch.Echo('Rar!  A monster is spawned!')

class cList(command):
    def doCommand(self,ch,world,args):
        ch.Push('---  COMMANDS ---')
        for cmd in ch.commands:
            ch.Push(cmd)
        ch.Prompt()


#An example of a command that no-one has, in order to get the 'you cannot'
#message. It should read "You cannot 'suck'!!"...
class cSuck(command):
    def __init__(self):
        self.name = 'suck'
    def doCommand(self,ch,world,args):
        ch.Push("Wow, you suck!")

# global command and alias hashes...
clist= {    'look':     cLook(),        
        'walk':     cWalk(),        
        'exits':    cExits(),        
        'say':        cSay(),            
        'time':     cTime(),        
        'fart':        cFart(),        
        'quit':        cQuit(),        
        'area':        cArea(),        
        'who':        cWho(),
        'py':        cPy(),
        'fight':    cFight(),
        'flee':        cFlee(),
        'atk':        cAtk(),
        'def':        cDef(),
        'mag':        cMag(),
        'score':        cScore(),
        'spawn':    cSpawn(),
        'list': cList(),
       }

galias={    'w':     'walk west',         
        'e':     'walk east',        
        'n':     'walk north',         
        's':    'walk south',        
        'l':     'look',            
        "'":     'say'            
       }
