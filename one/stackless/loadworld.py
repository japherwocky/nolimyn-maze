#from xml.sax import saxutils
from xml.sax import handler as defaultHandler
import string
from world import World,Area,Room,Exit,Func

world= World()
#the Handler gets passed the strings?
class loadRooms(defaultHandler.ContentHandler):

   def startDocument(self):
      self.tempRoom = ''
      self.tempExit = ''
      self.area = ''

      #dict of the rooms in the area, by id:Room
      self.rooms = {}
      #we use this to store text in between tags - see character():
      self.buffer = []

   def startElement(self,name,attrs):
      if name == 'room':
         self.tempRoom = Room(attrs.get('id'),attrs.get('title'))
      elif name == 'descrip':
         self.buffer=[]
      elif name == 'exit':
         self.buffer=[]
         self.tempExit = Exit(attrs.get('dir'),attrs.get('to'))
         if attrs.get('flags'):
            self.tempExit.flags = attrs.get('flags')
         if attrs.get('area'):
            self.tempExit.area = attrs.get('area')
      elif name == 'area':
         self.area = Area(attrs.get('id'),attrs.get('title'))  
      elif name == 'func':
         self.tempRoom.funcs[attrs.get('trigger')] = \
         Func(attrs.get('trigger'),attrs.get('fn'),attrs.get('params') )

      print 'Parsing %s' % (name)
      for attrName in attrs.keys():
         print 'Key:%s Value:%s' % \
         (attrName, attrs.get(attrName) )

   def characters(self,content):
      self.buffer.append(content)

   def endElement(self,name):
      if name == 'room':
         self.rooms[self.tempRoom.id] = self.tempRoom
      elif name == 'descrip':
         self.tempRoom.descrip=string.join(self.buffer)
      elif name == 'exit':
         self.tempExit.descrip=string.join(self.buffer)
         self.tempRoom.exits[self.tempExit.dir]=self.tempExit
      elif name == 'area':
         self.area.rooms = self.rooms
         world.areas[self.area.id]=self.area

   def endDocument(self):
      #i.e., </area>, see above
      pass

class loadPlayer(loadRooms):
   #pfiles generate personal rooms that need to be linked into !login.login
   def endDocument(self):
      arname = self.area.id.strip('~').lower()
      exit = Exit(arname,'password',self.area.id,'hidden')
      world.areas['!login'].rooms['login'].exits[arname] = exit


#this all makes it go.
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces
from os import listdir

parser = make_parser()

def boot():

   #Do I really need this?! - from some example. TODO, try it off
   parser.setFeature(feature_namespaces,0)

   for area in listdir('areas'):
      #to weed out '.svn', etc.
      if '.xml' in area:
         parseArea('areas/'+area)

   for player in listdir('players'):
      if '.xml' in player:
         parsePlayer('players/'+player)

   return world


def parseArea(xmlfile):
   parser.setContentHandler(loadRooms())
   parser.parse(xmlfile)

def parsePlayer(xmlfile):
   parser.setContentHandler(loadPlayer())
   parser.parse(xmlfile)

#This is obsolete, I think:
"""
#BUT, we still need to link the playerareas to the login area
def addPlayers():
   for area in world.areas:
      if '~' in area:
         ar = world.areas[area]
         arname = ar.id.replace('~','').lower()
         exit = Exit(arname,'password',ar.id,{'hidden':'all'})
         world.areas['!login'].rooms['login'].exits[arname] = exit
"""
