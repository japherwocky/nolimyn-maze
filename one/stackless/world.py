
#V 1.0 of the World
class World:
   def __init__(self):
      self.name = "The World"
      self.areas = {}
      #players, mobs, etc. are set as id:Player
      self.players = {}
      self.mobs = {}

   def __str__(self):
      return 'id:%s name:%s' % (self.id, self.name)

   def addPlayer(self,Player):
      self.players[Player.name] = Player
      return self
   def remPlayer(self,Player):
      try: del self.players[Player.name]
      except KeyError,key:
         #somehow we're trying to clear players twice on a quit.
         pass

   def addMob(self,Mob):
      self.mobs[Mob.name] = Mob
      return self
   def remMob(self,Mob):
      del self.mobs[Mob.name]

class Area(World):
   def __init__(self,id,name):
      self.id = id
      self.name = name
      self.rooms = {}
      self.players = {}
      self.mobs = {}

class Room(World):
   def __init__(self,id,name):
      self.id = id #maybe id is a ('computername','Human Name')
      self.name = name
      self.descrip = ''
      self.players = {}
      self.mobs = {}
      self.furniture = {}
      self.objs = {}
      #dict of exits, by dir:Exit
      self.exits = {}
      #dict of funcs, by trigger:Func
      self.funcs = {}

# class Road(Room)

#so..  should we have hidden/locked/etc?
#or, by virtue of the naming scheme..  (east)

class Exit:
   def __init__(self,dir,to,area='',flags=''):
      self.dir = dir

      #to in the format [area.]room
      self.to = to
      self.descrip = ''
      self.area = area
      
      #flags actually come in as a string - 
      #hidden [cmds.cExits()]: doesn't display hidden exits
      #excho [cmds.cWalk()]: when leaving, doesn't echo room name
      self.flags = flags

from funcs import flist
#Room-specific Functions
class Func:
   def __init__(self,keyword,fn,params):
      self.trigger = keyword
      self.fn = flist[fn]
      self.params = params
      pass
