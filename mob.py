"""
Maybe a class that's meant to run as a proc .. 
"""

from M import M, db
from random import shuffle
from uuid import uuid4

class StalkBot:
    def __init__(self, login):
        #pass a player to stalk 
        self.stalkee = login

        self.spawn()

    def spawn(self):
        playersheet = M[db].players.find_one( {'login':self.stalkee})
        x = playersheet['x']
        y = playersheet['y']
        z = playersheet['z']

        q = {
            'x':{'$gt':x-4, '$lt':x+4},
            'y':{'$gt':y-4, '$lt':y+4},
            'z': z,
            }

        players = M[db].players.find( q)
        blocks = M[db].cubes.find( q)

        #build indexed dict to check for blocking
        obstacles = {}
        for cube in blocks:
            obstacles[ '%d%d'%(cube['x'], cube['y'])] = cube

        for player in players:
            obstacles[ '%d%d'%(player['x'], player['y'])] = player


        #for possible cubes on screen, 
        allcoords = []
        for x in range( player['x']-3, player['x']+4):
            for y in range( player['y']-3, player['y']+4):
                allcoords.append( (x,y))

        shuffle( allcoords)
        goodcoord = None

        #very similar to how teleport works: should dump this algo into board.py somehow

        #shuffle and try to insert
        while allcoords:
            coord = allcoords.pop()        
            if '%d%d'%(coord[0],coord[1]) in obstacles:
                continue
           
            if M[db].cubes.find_one( {'x':coord[0],'y':coord[1],'z':playersheet['z']-1} ):
                goodcoord = coord
                break

        #dump our mob into Mongo
        z = {'login':'z'+ str( uuid4()).replace('-','') }
        self.x = z['x'] = goodcoord[0]
        self.y = z['y'] = goodcoord[1]
        self.z = z['z'] = playersheet['z']
        self.health = z['health'] = 2
        self.maxhealth = z['maxhealth'] = 3

        M[db].players.insert( z)

    def tick(self):
        info( 'tock')
        pass
        



if __name__ == '__main__':
    M = StalkBot( 'japherwocky')


