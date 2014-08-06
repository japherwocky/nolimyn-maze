import stackless, time


#so, Chronos.now is the given time
class Chronos:
   def __init__(self,ticklength=1):
      self.now = time.time()
      self.ticklength = ticklength
      print 'Initializing Chronos..'
      self.channel = stackless.channel()
      self.events = []
#     self.go()
   def go(self):
      #print 'Starting up teh clock.'
      #print self.events,len(self.events) 
      if len(self.events):
         alarm = self.events[0][0]
         if alarm <= self.now:
            channel = self.events[0][1]
            del self.events[0]
            channel.send(None)
      stackless.schedule()

      """
      while (len(events)) and (events[0][0]<= self.now):
         events[0][1].send(None)
         del events[0]
      """
      self.now = time.time()
      return True

   def tock(self):
      if self.now%self.ticklength == 0: return True
      else: return False

   def listen(self):
      print 'Chronos hears ALL.'
      while 1:
         msg = self.channel.receive()


#this puts a function to sleep for a bit.. can we set delays?
   def sleep(self,seconds):
      #print "chronos.sleep: %d seconds" % seconds
      
      channel=stackless.channel()
      alarm = self.now+seconds
      self.events.append( (alarm,channel) )
      self.events.sort()
      channel.receive() 


Chronos = Chronos()
#stackless.tasklet(Chronos.go)()
"""
willy = Sleeper(10)
billy = Sleeper(5)
stackless.tasklet(willy.sleep)()
stackless.tasklet(billy.sleep)()
"""
#stackless.run()
