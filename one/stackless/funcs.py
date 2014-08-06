#room-specific functions

import stackless

import string,traceback

#room specific functions, loaded from area files.
#params come from the <func /> as a string,
# args from the user as a list
class func:
   def __init__(self):
      self.name = 'command'
   def doCommand(self,ch,world,params,args):
      pass
   def spawnCommand(self,ch,world,params,args):
      stackless.tasklet(self.doCommand(ch,world,args))

class fFOO(func):
   def doCommand(self,ch,world,params,args):
      ch.Push('FOOOOOOO')
      ch.Push(params)
      ch.Push(string.join(args))
      ch.Prompt()

class respawn(func):
	def doCommand(self,ch,world,params,args):
		#set body to initialstats,
		#move to room/area in params
		ch.Prompt()

from player import createplayer

flist= { 'foo':            fFOO(),     \
         'newplayer':   createplayer() \
      }

