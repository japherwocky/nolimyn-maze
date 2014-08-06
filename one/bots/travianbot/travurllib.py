import conf
import urllib,urllib2
from os.path import join as urljoin

#So, first we'll load a page to get the login screen:
dumburl = urljoin(conf.baseurl,'dorf1.php')

#html = urllib2.urlopen( url ).readlines()

"""
#We potentially need to get the values of this dictionary's
keys.  Say, travian changes the login field to e1500d4 or something.
What the hell are those variable names, anyhow?
"""
loginconfs = {'w':'800:600', #or whatever, we could set this in conf
        'login':False, #uhh.. not sure what this is for either.
        'e1500da':conf.login, #this could probably change arbitrarily
        'e8a212c':conf.password,
        'eea1e0a':'',         #no idea what this is for..  start page maybe?
       }

headers = {'User-Agent':conf.useragent }

def login(url=dumburl,posts=loginconfs,headers=headers):
   req = urllib2.Request(url, urllib.urlencode(posts))
   req = urllib2.urlopen(req)
   headers['Cookie:'] = req.headers['set-cookie'].split(';',1)[0]
   return True

def getlogincookie(req):
   cookie = req.headers['set-cookie'].split(';',1)[0]
   headers['Cookie:'] = cookie



def geturl(url=dumburl):
   req = urllib2.Request(url)
   req.headers = headers
   req = urllib2.urlopen(req)
   return req.read()
   

