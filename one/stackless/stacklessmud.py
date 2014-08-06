# Inspired by code from richard.m.tew@gmail.com

import sys, traceback, weakref, logging,string
import stackless

import contrib.stacklesssocket
try:
   contrib.stacklesssocket.install()
except StandardError:
   pass
import socket

#Pidfile
import os
f = open('nolimyn.pid','w')
f.write( str(os.getpid()) )
f.close()



import loadworld
world = loadworld.boot()


#THE TICKER - SET TICK LENGTH IN chronos.py
import chronos
world.Chronos = chronos.Chronos
def Ticker():
   while world.Chronos.go():
      if world.Chronos.tock():
         for player in world.players:
            #spawn a doTick tasklet for each player
            stackless.tasklet(world.players[player].doTick)()
         stackless.schedule()
   print "oh no, Time has stopped!"

stackless.tasklet(Ticker)()


import player

class Connection:

   def __init__(self, clientSocket, clientAddress):
      self.clientSocket = clientSocket
      self.clientAddress = clientAddress

      self.readBuffer = ""

      #inits and makes self a Player
      player.Player(self,world)



   def Disconnect(self):
      """
      if self.disconnected:
         raise RuntimeError("Unexpected call")
      """
      self.disconnected = True
      self.clientSocket.close()

   def Write(self, s):
      try: self.clientSocket.send(s)
      except: #oops, nobody is there
         logging.info('Discod')

   def ReadLine(self):
      global server

      s = self.readBuffer
      while True:
         # If there is a CRLF in the text we have, we have a full
         # line to return to the caller.
         if s.find('\r\n') > -1:
            i = s.index('\r\n')
            # Strip the CR LF.
            line = s[:i]
            self.readBuffer = s[i+2:]
            while '\x08' in line:
               i = line.index('\x08')
               if i == 0:
                  line = line[1:]
               else:
                  line = line[:i-1] + line[i+1:]
            return line

         # An empty string indicates disconnection.
         v = self.clientSocket.recv(1000)
         if v == "":
            self.disconnected = True
            raise player.RemoteDisconnectionError
         s += v

class Server:
   def __init__(self, host, port):
      self.host = host
      self.port = port

      print 'Server.__init__: %s %s'%(self.host,self.port)
      #initializes and runs itself as a tasklet
      stackless.tasklet(self.Run)()

   def Run(self):
      listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      listenSocket.bind((self.host, self.port))
      listenSocket.listen(5)
      
      print 'Accepting connections on %s %s'%(self.host,self.port)
      logging.info("Accepting connections on %s %s", self.host, self.port)
      #so, when someone connects, it makes them a Connection()
      try:
         while True:
            clientSocket, clientAddress = listenSocket.accept()
            Connection(clientSocket, clientAddress)
            #so Connection() makes a Player() which makes a tasklet..
            stackless.schedule()

      except:  
         traceback.print_exc()



def Run(host, port):

   global server
   server = Server(host, port)
   while 1:
      print 'RUN STACKLESS, RUN'
      stackless.run()

if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

	try:
		print 'Launching on locahost:1399'
		Run("0.0.0.0", 1399)
	except KeyboardInterrupt:
		logging.info("Server manually stopped")

