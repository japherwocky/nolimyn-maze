#!/usr/bin/env python

"""Online RPS client module by David Bau
http://davidbau.com/rps/

This code is in the public domain.  You are free to use it as you
like, and it comes with no warranties.  So your mileage may vary.
RPS clients can play in the RPS arena at http://davidbau.com:8088/.

To play a match, just do this:

for turn in xrange(rps.turns):
  <theirmove> = rps.play(<mymove>)

The moves are 0 for rock, 1 for paper, 2 for scissors.

Winning consistently against good players is harder than it looks.
"""

import os, sys, random

rps = ['rock', 'paper', 'scissors']

def beat(i):
  return (i + 1) % 3
def loseto(i):
  return (i - 1) % 3

if os.getenv('GATEWAY_INTERFACE') is not None:
  import urllib, cgi, cgitb, traceback; cgitb.enable()

  def play(my):
    global url
    return rps.index(urllib.urlopen(url + "?play=" + rps[my]).read().strip())

  def setup():
    global url, turns, seed
    fields = cgi.FieldStorage()
    if not fields and hasattr(sys.modules['__main__'], '__file__'):
      text = file(sys.modules['__main__'].__file__).read()
      sys.stdout.write("Content-Type: text/plain\r\n"
                       "Content-Length: %d\r\n\r\n%s" % (len(text), text))
      sys.exit(0)
    url = fields.getfirst('url', None)
    turns = int(fields.getfirst('turns', '-1'))
    seed = fields.getfirst('seed', None)
    if url is None or turns <= 0 or turns > 10000:
      raise Exception("Bad input")
    if seed is not None:
      random.seed(int(seed))
    sys.stdout.write("Content-Type: text/plain\r\n\r\nrps\n")
    sys.stdout.flush()

elif len(sys.argv) > 1:
  import optparse, urllib, atexit

  def setup():
    global url, turns, wins
    parser = optparse.OptionParser(
      'usage: \%prog --arena <arenaurl> <opponent> <turns>')
    parser.add_option('', '--arena', dest='arena',
      default='http://davidbau.com:8088/single', help='Arena server to use')
    options, args = parser.parse_args()
    opponent = args[0]
    turns = (len(args) == 1) and 100 or int(args[1])
    url = urllib.urlopen(options.arena + '?player=%s&turns=%d' %
      (urllib.quote(opponent), turns)).read().strip()
    wins = [0, 0, 0]
    atexit.register(finish)
  
  def play(my):
    global url
    their = rps.index(urllib.urlopen(url + "?play=" + rps[my]).read().strip())
    wins[(my - their) % 3] += 1
    sys.stdout.write(''.join([rps[i][0] for i in [my, their]]))
    sys.stdout.write(' ')
    sys.stdout.flush()
    return their

  def finish():
    if sum(wins):
      sys.stdout.write('\nWins: %d\nLosses: %d\nTies: %d\nScore: %.3f\n' % (
        wins[1], wins[2], wins[0],
        float(2 * wins[1] - wins[2] - wins[0]) / sum(wins)))

else:
  import atexit

  def setup():
    global url, turns, wins
    url = ''
    turns = 100
    wins = [0, 0, 0]
    atexit.register(finish)

  def play(my):
    their = random.randrange(3)
    wins[(my - their) % 3] += 1
    sys.stdout.write(''.join([rps[i][0] for i in [my, their]]))
    sys.stdout.write(' ')
    sys.stdout.flush()
    return their

  def finish():
    if sum(wins):
      sys.stdout.write('\nWins: %d\nLosses: %d\nTies: %d\nScore: %.3f\n' % (
        wins[1], wins[2], wins[0],
        float(2 * wins[1] - wins[2] - wins[0]) / sum(wins)))

setup()    
