triggers = [
	'\n\r',
	'By what name do you wish to be known, traveller?',
	'traveller',
	'Return to continue'
	]

LOGIN = 1
WANDER = False


#whatever data the mud has sent - lines are marked with \n\r :(
def proc(intuple):
	index,regexobj,str = intuple
	import sys
	sys.stdout.write( str )
	#logfile.write( str)
	if LOGIN: 
		return login(str) #crappy logic flow
	else: 
		return serve(str)

def login( str ):
	global LOGIN
	if 'traveller' in str:
		return open('/home/japherwocky/.logins/empowerserv').read()

	if '[Hit Return to continue]' in str:
		LOGIN += 1
		if LOGIN > 2: LOGIN = False
		return '\n'

	if 'Reconnecting. Type replay to see missed tells' in str:
		LOGIN = False
		print 'Reconnect detected.'
		return 'look'

import re
exittrig = re.compile(r"^\[Exits: ([northeawsupd \(\)]*)\]")

stalledtrig = re.compile(r"You are hungry.")
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
	
	foo = stalledtrig.match(str)
	if foo:
		return 'look'

hello = re.compile(r'([\w]*) awakens into the world of Shalar.')
empowerme = re.compile(r'^([\w]*) pounces on you and >>> TAGS <<< you!')
empowered = re.compile(r'.*They are already empowered')
empowered2 = re.compile(r'.*You have EMPOWERED ([\w]*)')
def serve(str):
	status = hello.match( str)
	if status:
		empoweree = status.groups()[0].lower()
		return 'tell %s Hi - tag me if you need to be empowered.' % empoweree

	status = empowerme.match( str)
	if status:
		empoweree = status.groups()[0].lower()
		return 'empower %s yes' % empoweree
	#print empowered.match( str) 
	#print empowered2.match( str)

	if empowered.match( str) or empowered2.match( str): return 'wink'
