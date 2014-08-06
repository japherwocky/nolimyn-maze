from combat import Body
import player
import cmds
from StringIO import StringIO
from prompt import Prompt
class Monster(player.Player):
   def __init__(self,world, area='!login', room='login'):
      #assign an id.. this should probably work differently.
      #this is the PLAYER name, until a login.
      """
It would be nice if the 'id' represented a prototypical monster.  How do we handle name collisions?

           sdesc                     name
A fire-breathing dragon is here.  [firedragonX]
      """
      self.id = str( id(self) )
      self.name = 'Monster' 
      self.monster = True

      self.body = Body(self)

      self.world = world.addMob(self)
      self.area = world.areas[area].addMob(self)
      self.room = self.area.rooms[room].addMob(self)

      self.buffer = StringIO()
      #set the prompt and commands..
      self.Prompt = Prompt(self)

      #so, players can lose/gain commands on the fly!
      self.commands = cmds.clist
      self.parseCommand('look')
   def Move(self,room,area=''):
      try:
         if area:
            #move areas
            self.area.remPlayer(self)
            self.area = self.world.areas[area].addPlayer(self)
         #move rooms
         self.room.remPlayer(self)
         self.room = self.area.rooms[room].addPlayer(self)

         self.parseCommand( 'look' )
      except KeyError:
         logstr = 'moving %s to %s from room:%s in area:%s'
         if (type(room)!=type('')) or (type(area)!=type('')):
            print 'Try passing in a string, smartass'
            #TODO: maybe check if it's an area, find the name
            logstr %= (self.id,'non-string',self.room.id,self.area.id)
            logging.warning(logstr)
         else:
            logstr %= (self.id,'nowhere room',self.room.id,self.area.id)

         logging.error(logstr)

      except:
         print 'Error moving',self.id,'to',room,area



   #   WRITE FUNCTIONS
   def Write(self,msg):
      try:
         self.buffer.write(msg)
      except:
         raise

   def doTick(self):
      #self.Echo('TICK')
      pass


