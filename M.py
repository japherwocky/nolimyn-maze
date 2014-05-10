#this should probably go in nolimyn.py


import pymongo
M = pymongo.Connection()
db = 'noldb'


"""
This is a convenient way to keep this global and dodge
circular imports

The index is the players, by login name, and the values
are either a callback function (the client is waiting for
data), or a list of rendering instructions (bits of javascript
to be eval'd)
"""

Players = {}
