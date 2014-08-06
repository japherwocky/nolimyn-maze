"""

so.. command is parsed, let's say

ch.status = { 'fighting' : opponent }

where opponent is a Player() 

Ticks are once a minute maybe.. 20rounds/tick
fight should be a minimum of 13 rounds?


HIT defeats SPECIAL defeats BLOCK

HIT = DAMAGE

							 SPECIAL 
						/				\
		DoT		Maledict

if we have STR proportional to DEX
and INT prop. to WIS

STR determines HIT dmg
DEX determines BLOCK (counter dmg) [or DODGE (heal?)]
INT determines MALEDICT dmg
WIS determines DOT dmg

reverse that, so you get STAT ALLOCATION POINTS, per level:
5,3,2,1,1

and start with 1 of everything.. so 13 is MAX STAT

if you have 100 life, 
one MAX STAT attack does 1/5 dmg
one MIN STAT attack does 1/13 dmg

so.. you could be 6/4/3/3

what if MAX STAT did 18 dmg, and MIN STAT did 1 dmg

at 1rd/second, LONGEST fight would be 1:40

FASTEST possible would be :06 .. 

DoT MAX = +9 per round
Cripple MAX = -9 per round

bonus chart, by class?
	 HIT	BLOCK	DoT	MAL
M |							cripple
C |		  heal
T |					poison
W | bash

each equiv. to 1 respective round..

fastest possible would be :03  ?
got to work out the ramifications of cripple, I think

hp/ma/mv

str = dex, int = wis = 5 hp = 5 ma = 10 mv = 18/5 sec
hp = ma = 2mv

1 round (sec) = MAXSTAT hp (18)


1 DoT = 18 hp/5sec ,  compounded each round! 
MAL = 1 stat ... how do you put a value on this?
		average fight length, * 


1 HIT = 18hp/sec = 1 BLOCK

M = C, W = T
W>M>T	M>W>C
W<C<T	M<T<C

Suddenly, you are attacked! Do you:

< hit/block/special[maledict/DoT] (:5)>

----
further thoughts, 24feb08:

atk/def - a successful defense adds a (stackable) multiplier to next attack/special, based on relative dex (defender - attacker)

str: atk damage & health
dex: defense multipliers
int: #of spells/specials, xp multiplier
wis: strength of specials, mana

specials:
+/- str, dex, int, wis, hp, mana, mvs

stats max at 13!, begin at level 1 - allocation points per level, 5,3,2,1,1, and start with 8 free in creation.  (Lvl0 = newbie, lvl-1=ghost)

level of mob determines (inverseley) # of seconds to respond, in Live mode.
lvl1 = 5 second delay, lvl5 = 1.

to reward quickness, points awarded for quickness.  i.e., you respond to a lvl1 monster in 1 second, you receive 4 points.  Kill = mob level * int

in PvP, use highest player's level?  Bill(4) v. Larry(1) .. Larry gets 1 second, Bill gets 4
"""
"""
13may08 - props to jarod malbone for some mad pingpong

ok, continuing from above - your level is how fast you can respond: 1 input 
per X/x seconds, where X is the max level and x is your current level.

your attack/defend queue always contains at least your last input - so higher levels get free shots on lower levels.

or another way, Larry's attack takes 1 second, Bill's takes 4.
"""


import stackless


#so.. if we pass in bodies as attackers and victims.. a Body would look like:



#how many allocation points per level. statchart[level]
statchart = (8,5,3,2,1,1)

#The body holds the stats, maybe the location in the world?
#orrr.. spirit and body have locations, if spirit not in room
#with body, body is a corpse.  or zombie!



#Mind represents the combat AI, to carry the metaphor.
class Mind:
	def __init__(self,body=False,skillz=False,mem={}):
		self.body = body
		#Store a [] of atks 
		self.mem = mem

		if not skillz: skillz = ['atk']
		self.skillz = skillz

	def nextatk(self):
		#so, here we define combat logic

		#for now, THROW ROCK.
		return self.skillz[0]

	#expects opponent as an identifying string.
	#perhaps this should get both an id and a class v. mobs?
	def remember(self,opponent,atk):
		if opponent in self.mem: self.mem[opponent].append(atk)
		else: self.mem[opponent] = [atk,]


"""
So that means.. we have max stats and stats (current!) 
On birth(), stats go to max! maybe a bit more.
"""
def buildstats():
	capstats = (  'str', #atk damage and max health
			'dex', #to calculate multipliers
			'int', #number of specs, xp multiplier
			'wis', #magnitude of specs
			'hp',  #health
			'mp',  #mana/magic/mojo
			'mv',  #moves
		)

	stats = (
		'ap', #stat allocation points
		'xp', #experience
		'$', #cash on hand
		'lvl', #level
		'atk', #current attack, used by Quiver()
		'atkq', #upcoming attacks
		)
		


	initstats = {}
	for x in stats: initstats[x] = 0
	for x in capstats: initstats[x] = -1
	for x in capstats: initstats['max'+x] = 1
	initstats['atk'] = 'atk'
	initstats['atkq'] = []
	return initstats

class Quiver:
	def __init__(self, stats, quiver=False):
		self.stats = stats
		if not quiver: 
			self.quiver = {0:'hp'}
			self.arrows = ['hp']
		else: self.quiver = quiver
		self.index = False

	def getAtk(self):
		return self.quiver[self.index]

	def scrollAtk(self, fwd=True):
		if fwd:
			self.index = (self.index +1) % len(self.quiver)
		else:
			self.index = (self.index -1) % len(self.quiver)

	def addAtk(self,atk):
		if len(self.quiver) <= self.stats['int']:
			self.quiver[len(self.quiver)] = atk
			if not atk in self.arrows: self.arrows.append(atk)
			return True
		else: return False


	def checkAtk(self,atk):
		return atk in self.arrows

#spirit will be a .. Player() object
class Body:
	 
	def __init__(self, spirit, stats=False, mind=Mind()):
		from copy import copy
		self.stats = stats if stats else buildstats()
		self.maxstats = copy(stats)
		self.spirit = spirit
		self.mind = mind
		self.atkq = [];self.setatk()
		self.atk = self.atkq[0]

		self.fights = []

	
	def begin(self):
		from time import time
		from copy import copy
		self.stats = copy(self.maxstats)
		self.stats['birth'] = time()
		self.stats['age'] = 0

	def end(self):
		from time import time
		self.death['death'] = time()

	def setatk(self, atk=False):
		if not atk: 
			self.atkq.append(self.mind.nextatk())
		else: self.atkq.insert(0,atk)

		#prompting updates are handled in cmds.py
		

	def getatk(self):
		"""
		if not self.atkq: atk = self.mind.nextatk()
		else:atk = self.atkq.pop()
		self.atk = atk
		self.spirit.prompt = '<%s >'%atk
		return atk
		"""
			
		if len(self.atkq) > 0:
			atk = self.atkq.pop()
		else: atk = self.atk

		self.atk = atk
			
		if hasattr(self.spirit, 'monster'):
			stackless.tasklet(self.setatk)()
			#stackless.schedule() #should get scheduled by returning to pulse()
		else:
			self.stats['atkq'] = self.atkq
			self.stats['atk'] = self.atk
		return atk

"""
This should.. just inherit Player() and overwrite the networking stuff
so that we can override a mob and do talk and shit.
"""
#this got moved to monsters.py
"""
class Mob:
	def __init__(self,stats=False,mind=Mind(),name=False):
		self.id = str( id(self) )
		if name: self.name = name
		else: self.name = 'Foomonster'+self.id

		self.body = Body(self,stats,mind)

		self.mob = True
	def Echo(self,*args): pass
"""

import stackless
from cmds import lEcho
#ok, we are only going to pass in attacker and victim as Body()s
class NeoFight:
	def __init__(self,attacker,victim):
		attacker.fights.append(self)
		victim.fights.append(self)
		self.fighting = True

		#ugh, check levels:
		def checkLevel(me):
			if me['lvl'] < 1: me['lvl'] = 1
		checkLevel(attacker.stats)
		checkLevel(victim.stats) 

		#maybe we just need attacker.body
		self.attacker,self.victim = attacker,victim
		self.room, self.world = attacker.spirit.room,attacker.spirit.world


		lEcho('A fight breaks out!',self.room)

		stackless.tasklet(self.pulse)(attacker,victim)
		#stackless.tasklet(self.pulse)(victim,attacker)
		stackless.tasklet(self.initpulse)(victim,attacker)
		stackless.schedule()

	def pulse(self,me,victim):
		t = 5.0 / me.stats['lvl']
		while self.fighting:
			#print 'Pulsing for %s, %d seconds'%(me.spirit.name,t)
			self.fight(me,victim)
			#me.setatk()
			self.world.Chronos.sleep(t)

	#so that combat rounds are slightly offset
	def initpulse(self,me,victim):
		self.world.Chronos.sleep(.3)
		self.pulse(me,victim)

	#gets bodies from pulse
	def fight(self,attacker,victim):
		atk = attacker.getatk()
		victim.mind.remember(attacker.spirit.name,atk)
		vic = victim.atk

		def setint(atk):
			#print 'Splitting: %s'%atk
			if atk == 'atk': return 1
			elif atk == 'def': return 2
			else: return 3

		def wincheck(atk,vic):
			if atk == vic: return 'tie'
			elif (atk-vic == 1) or (atk-vic == -2): return 'win'
			elif (vic-atk == 1) or (vic-atk == -2): return 'lose'
	
		attacker.spirit.Push('\nYou attempt %s on %s..'%(atk, victim.spirit.name))
		victim.spirit.Push('\n%s attempts %s on you..' % (attacker.spirit.name,atk))
		result = wincheck(setint(atk),setint(vic))
		try:
			if result == 'win':win(atk,attacker,victim)
			elif result == 'lose':win(atk,victim,attacker)
			elif result == 'tie':tie(atk,attacker,victim)
		except:
			self.fighting = False
			

#so.. actually - we need to not let them level up, etc. while fighting?
#attacker and victim are 
def win(atk,attacker,victim):
	attacker.spirit.Echo('Your %s wins this round! (win!)'%attacker.atk)
	victim.spirit.Echo('You are no match for %s\'s %s. (lose!)'%(attacker.spirit.name,atk))

def tie(atk,attacker,victim):
	attacker.spirit.Echo('%s blocks your %s with one of the same! A tie!'%(victim.spirit.name,atk))
	victim.spirit.Echo('You block %s with your own %s!'%(attacker.spirit.name,atk))

rock = 1
paper = 2
scissors = 3

"""
So, dictionaries like: atkv{'atk':tiefunc,'def':losefunc,'mag':winfunc}

	getattr(self,''.join(atk,'v')(self.attacker,self.victim,atk)

rsp comp uses:

		  if (verbose1) { printf(" p1 = %d, p2 = %d", p1, p2); }
		  if (p1 == p2) {
				ties++;
				if (verbose1) { printf(" tie!\n"); } }
		  else if ( (p1-p2 == 1) || (p1-p2 == -2) ) {
				p1total++;
				if (verbose1) { printf(" p1 wins!\n"); } }
		  else if ( (p2-p1 == 1) || (p2-p1 == -2) ) {
				p2total++;
				if (verbose1) { printf(" p2 wins!\n"); } }
		  else printf("Error: should not be reached.\n");

"""
								


###  deprecated!

class Fight:
	def __init__(self, attacker,victim,world):
		attacker.fights.append(self)
		victim.fights.append(self)

		self.attacker,self.victim,self.world = attacker,victim,world
		#maybe the initial attackqueue is random
		#and the initial defendqueue is weighted to karma
		self.attackqueue,self.defendqueue = [],[]

		#probably a stackless.tasklet(self.pulse)() here.. no
		#register the fight with chronos, it'll send the pulses

	def pulse():
		#fight starts pulsing - fight() each, by comparing queues
		self.fightround(self.checkqueue())
		pass

	#so, each tick, it sends a prompt to each player, and checks their command queue

	def checkqueue(self):
		if (len(self.attackqueue) > 1):
			if (len(self.defendqueue) > 1):
				return self.attackqueue.pop(0), self.defendqueue.pop(0)
			elif ( len(self.defendqueue) == 1 ):
				return self.attackqueue.pop(0),self.defendqueue[0]
		elif (len(self.attackqueue == 1)):
			if (len(self.defendqueue) > 1):
				return self.attackqueue[0],self.defendqueue.pop(0)
			elif len(self.defendqueue) ==1:
				return self.attackqueue[0],self.defendqueue[0] 

	def fightround(attack,defense):
		if attack == 'atk':
			if defense == 'atk':
				#tie - maybe check relative str for mv loss
				pass
			elif defense == 'def':
				#lose
				#self.defender.multiplier += 1
				#self.defender.defend(self.attacker)
				pass
			elif defense == 'spec':
				#win - do self.attacker.attack(self.victim)
				#As your foe gathers the strength for a spell, you pounce!
				pass
		elif attack == 'def':
			if defense == 'def':
				#tie - check relative dex for mv loss
				#You circle your foe, searching for a weakness to exploit.
				pass
			elif defense == 'spec':
				#lose
				#self.defender.special(self.attacker)
				pass
			elif defense == 'atk':
				#win
				#self.attacker.multiplier += 1
				#self.attacker.defend(self.defender)
				pass
		elif attack == 'spec':
			if defense == 'spec':
				#tie - check relative .. mana levels? wis!
				pass
			elif defense == 'atk':
				#lose
				#self.defender.attack(self.attacker)
				pass
			elif defense == 'def':
				#win
				#self.attacker.special(self.defender)
				pass


"""
So it's rock paper scissors, with stats.
"""
