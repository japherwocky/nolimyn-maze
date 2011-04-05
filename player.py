"""
Represents a connection to the game; tracks account info,
parses incoming content and receives text to go to the
client
"""

import string,traceback,os,collections,time
from commands import Commands
from settings import dbconn as db

import pymongo
M = pymongo.Connection()

import cPickle

class Player:
    p = '<%(hp)s/%(mhp)shp %(mp)s/%(mmp)smp>'


    def __init__(self, user):
        self.buffer = collections.deque()
        self.waiter = False #callback waiting for lists/messages

        self.user = user

        self._load()

    def _load(self):

        user = M.noldb.players.find_one( {'login':self.user})

        if not user:
            raise 

        self.scoresheet = user

        from body import PlayerBody
        self.Body = PlayerBody( self) # self.Body = Body.load( user)

        #set them into the right Board/Room from nolimyn.py

    def save(self):
        M.noldb.players.save( self.scoresheet)

    def __str__(self): return self.user


    #to do snoops / multiple listeners, wrap these methods        
    def write( self, msg):
        """expects things one line at a time"""
        self.buffer.append( msg)
        if self.waiter:
            self.read( self.waiter)
            self.waiter = False

    def read( self, callback):
        """client is ready for some datas, send whatever we have"""
        if self.buffer:
            callback( list(self.buffer))
            self.buffer.clear()
        else: self.waiter = callback


    def Parse( self, data):
        """
        Commands are functions or classes that take Player, args as a string
        TODO:, strip javascript/html/xml out 
        """
        self.buffer.append( '>'+data)
        if not data or data=='\n': #sent '' or somesuch
            self.write( self.prompt())
            #self.Prompt() 
            return

        if self.Body.lag > time.time():
            #self.write( str( time.time()))
            self.Body.lagq.append( data)
            return

        #first word is the command, anything else is args
        data = data.lstrip('>')
        if not data: data = '>'
        args = string.split( data )
        command = args[0]
        args = args[1:]


        try: 
            Commands[command](self, args)
        except KeyError:
            for cmd in Commands.keys():
                if cmd.startswith( command):
                    Commands[cmd](self, args)
                    break

            self.write( '%s ?' % command)


    def Quit(self):
        #self.Board.logout( self.serverid) #er.. wha? TODO
        del self
        

        


class Anonybot(Player):
    def __init__(self, user):
        self.buffer = collections.deque()
        self.waiter = False #callback waiting for lists/messages

        self.user = user

        from telnetlib import Telnet
        host = 'godwars2.org'
        port = 3000

        try:
            self.T = Telnet()
            self.T.open( host, port)
            self.connected = True
        except:
            self.connected = False

        #heartbeat uses this to calc delays
        self.idle = 1
        self.lastpulse = time.time()

    def pulse(self):

        try:        
            self.Parse( self.proc( self.T.read_very_eager()))
        except EOFError:
            self.connected = False

        self.lastpulse = time.time()

    #override for triggers, AI
    def proc( self, data): 
        if data:
            data = data.replace('\r','')
            self.write( data)
            self.idle = 1
        return False

    def Parse(self, data):
        if not data: return

        self.T.write( str(data)+'\n') #cast to str(), unicode fucks it
        self.idle = 1
        self.write( '>'+str(data))

