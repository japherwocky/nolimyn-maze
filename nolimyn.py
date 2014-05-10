#!/usr/bin/env python

import logging
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import json, os

from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)


from M import M, db, Players
from commands import parse

class Application(tornado.web.Application):

    logins = {}

    def __init__(self):

        """
        Basically, the client POSTs commands to Send, and gets rendering instructions
        via /recv via comet style polling
        """

        handlers = [
            (r"/", Canvas), #load the initial template
            (r"/recv", Recv), #GET: browser recvs updates  POST: other servers communicate?!
            (r"/send", Send), #browser sends commands
            #maybe sendbot
            (r"/logout/?", AuthLogoutHandler),
            (r"/login/?", LoginHandler),
        ]

        settings = dict(
            cookie_secret="43oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/login",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

from tornado.template import Loader
Loader = Loader('templates')
class BaseHandler(tornado.web.RequestHandler):
    
    def get_current_user(self):
        #doing self.current_user calls this (then caches)
        user_json = self.get_secure_cookie("user")
        if not user_json: return None
        return tornado.escape.json_decode(user_json)

    @property
    def user(self): return self.get_current_user()

    def render( self, template, **kwargs):
        kwargs['user'] = self.user
        self.finish( self.render_string( template, **kwargs))




import board

class Canvas( BaseHandler):
    """
    Load the template
    """
    @tornado.web.authenticated
    def get(self):

        """
        if not self.user in Players:
            Players[ self.user] = False
            #spawn

        P = M[db].players.find_one({'login':self.user}) 
        cubes = board.rendercubes( P['x'], P['y'], P['z'])
        players = board.renderplayers( P['x'], P['y'], P['z'])
        health = board.renderhealth( self.user)
        deck = board.renderdeck( self.user)
        #add a list of javascript statements to Players[self.user]
        Players[self.user] = cubes + players + health + deck
        """

        self.render('canvas.html') 




class Recv( BaseHandler):
    """
    Client subscribes to this to get new rendering instructions
    maybe /"events"
    """

    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        #dev:
        if self.user not in Players or not Players[self.user]:
        #if not Players[self.user]:
            #if no messages, set a callback
            Players[self.user] = self.push
        else:
            try:
                self.push( Players[self.user])
            except:
                raise

    def push( self, messages):
        # Closed client connection
        if self.request.connection.stream.closed():
            del Players[self.user]
            return

        Players[self.user] = False

        self.finish( json.dumps(messages))


class Send( BaseHandler):
    """
    client sending args to us
    """

    @tornado.web.authenticated
    def post( self):
        txtin = self.get_argument('input')
        parse( txtin.lower(), self.user)


from hashlib import sha256
class LoginHandler(BaseHandler):
    # pull this out of a BASH env or something
    magic = 'ef47862869f311de943f001e4c8e3a11'

    def get(self, errormsg=None):
        #send the generic login screen
        self.render('login.html', errormsg=errormsg, xsrf=self.xsrf_token)

    def post(self):
        login = self.get_argument("login", None)
        password = self.get_argument("password", None)

        if not login and not password:
            errormsg = "please enter a name and a password"
            return self.get( errormsg)

        #make hash to compare
        password = sha256(password+self.magic).hexdigest()
        user = M.noldb.players.find_one( {'login':login})

        if user:
            #check the password
            if password == user['passhash']: self._on_auth(login)
            else:
                return self.get( "password denied")

        else:
            #create new player someday
            """
            M.noldb.players.insert( {
                'login':login, 
                'passhash':password, 
                'x':0, 'y':0, 'z':1,
                'inventory': [],
                'equipped': {},
                })
            """

            self._on_auth(login)

    def _on_auth(self, user):
        self.set_secure_cookie("user", tornado.escape.json_encode(user))
        self.redirect("/")


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.write("You are now logged out")


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    print 'Booting on port 8888'
    main()
