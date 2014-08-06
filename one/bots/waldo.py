triggers = [
	'\n\r',
	'By what name do you wish to be known, traveller?',
	'traveller',
	'Return to continue'
	'<[\d]{0,4}hp [\d]{0,4}m [\d]{0,4}mv ->'
	]

LOGIN = True
WANDER = False

#some logging :)
#logfile = open('/tmp/waldo.log','a')


#whatever data the mud has sent - lines are marked with \n\r :(
def proc(intuple):
	index,regexobj,str = intuple
	import sys
	sys.stdout.write( str )
	#logfile.write( str)
	if LOGIN: 
		return login(str) #crappy logic flow
	else: 
		return wander(str)

def login( str ):
	global LOGIN
	if 'traveller' in str:
		return 'Waldo\ncowman\n'

	if '[Hit Return to continue]' in str:
		LOGIN = False
		return '\n'

	if 'Reconnecting. Type replay to see missed tells' in str:
		LOGIN = False
		print 'Reconnect detected.'
		return 'look'

import re
exittrig = re.compile(r"^\[Exits: ([northeawsupd \(\)]*)\]")

stalledtrigs = [
	 re.compile(r"You are hungry."),
	 re.compile(r"You are thirsty."),
 	re.compile(r"Nah... You feel too relaxed..."),
 ]

guildtrigs = [
re.compile(r"I cannot allow you to pass."),
re.compile(r"The zealot guildguard growls and fiercely shakes his head at you"),
re.compile(r"slowly draws his sword, shaking his head silently"),
re.compile(r"The healer guildguard shakes his head silently."),
re.compile(r"guildguard says"),
re.compile(r"A rustle in a nearby bush alerts you to a ranger's angry eyes."),
re.compile(r"The Guardian Hunter growls and blocks the way inward."),
re.compile(r"The anti-paladin guildguard shoves you backward with a smirk."),
re.compile(r"The shapeshifter guildguard bares his still very human teeth at you."),
re.compile(r"You are not of the guild."),
re.compile(r"You don't belong in there"),
]

def wander( str ):
	from random import choice
	foo = exittrig.match( str )
	if foo:
		exits = foo.groups()[0].split(' ')
		#avoid doors
		exit = choice( exits )
		if '(' in exit:
			while '(' in exit:
				exit = choice(exits)
			return exit
		else:
			return exit
	
	for guildtrig in guildtrigs:
		foo = guildtrig.search(str)
		if foo:
			return 'look'

	#foo = stalledtrig.match(str)
	for stalltrig in stalledtrigs:
		foo = stalltrig.search(str)
		if foo:
			return 'stand\nlook'



