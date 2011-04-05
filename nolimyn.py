#!/usr/bin/env python

import logging
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import os.path
import uuid, sqlite3

from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)

import pymongo
M = pymongo.Connection()

class Application(tornado.web.Application):

    def __init__(self):

        handlers = [
            (r"/", MainHandler),
            (r"/logout", AuthLogoutHandler),
            (r"/login", LoginHandler),
            (r"/a/message/new", MessageNewHandler),
            (r"/a/message/updates", MessageUpdatesHandler),
        ]
        settings = dict(
            cookie_secret="43oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/login",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    
    def get_current_user(self):
        #doing self.current_user calls this (then caches)
        user_json = self.get_secure_cookie("user")
        if not user_json: return None
        return tornado.escape.json_decode(user_json)

    @property
    def user(self): return self.get_current_user()

    def render(self, template, **kwargs):
        kwargs['xsrf'] = self.xsrf_token
        kwargs['user'] = self.user
        kwargs['request'] = self.request
        kwargs['title'] = B.book['title']
        kwargs['author'] = B.book['author']
        html = template.generate( **kwargs).render('html', doctype='html')
        self.finish( html)


from templates import Main
from player import Player
from time import time
class MainHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):

        if not self.user in MessageMixin.players:
            player = MessageMixin.players[ self.user] = Player( self.user)
            #scan Player.progress for the board/room to spawn them in

            if not player.progress.keys():
                player.progress = {0:0}
            level = max(player.progress.keys())
            if not B.boards[level].spawn( MessageMixin.players[self.user].Body, Room=B.boards[level].maze[ B.boards[level].solution[player.progress[level]]]):
                B.boards[level].spawn( MessageMixin.players[self.user].Body)
        else:
            #already playing, but reloaded for whatever reason
            player = MessageMixin.players[self.user]
        tornado.ioloop.DelayedCallback( lambda: player.Parse('look'), 500).start()
        tornado.ioloop.DelayedCallback( lambda: player.Parse('read'), 700).start()

        #self.render( Main, messages=MessageMixin.players[ self.user].read())
        self.render( Main)

        user = M.noldb.players.find_one( {'login':self.user})
        user['lastseen'] = time()
        M.noldb.players.save( user)



class MessageMixin(object):
    """
    Pass messages through here, expects something like:    
        msg = {'id':str(uuid4()),'to':self.serverid, 'from':'', 'body':msg}
        msg['html'] = '<div class="message" id="%s">%s</div>' % ( msg['id'], msg['body'])
    """
    players = {} #maps {'user':Player()}
    
    def wait_for_messages(self, callback, cursor=None):
        #check if some are waiting?

        Player = MessageMixin.players[ self.user]
        if Player.waiter:
            Player.read( Player.waiter)
        else:
            Player.read( callback)
        if cursor:
            pass
            #import pdb;pdb.set_trace()
        Player.read( callback)

    @classmethod
    def new_messages(self, user, messages):
        #don't grok why, but calling self.user in here doesn't work
        for cmd in messages:
            try:
                MessageMixin.players[ user].Parse( cmd)
            except:
                logging.error('Error parsing %s'%messages, exc_info=True)

        
        """
        cls = MessageMixin
        logging.info("Sending new message to %r listeners", len(cls.waiters))
        for callback in cls.waiters:
            try:
                callback(messages)
            except:
                logging.error("Error in waiter callback", exc_info=True)
        cls.waiters = []
        cls.cache.extend(messages)
        if len(cls.cache) > self.cache_size:
            cls.cache = cls.cache[-self.cache_size:]
        """

class MessageNewHandler(BaseHandler, MessageMixin):
    @tornado.web.authenticated
    def post(self):
        cmd = self.get_argument("body")

        if self.get_argument("next", None):
            self.redirect(self.get_argument("next"))
        else:
            html = '<div class="message" id="%s" style="display:none"></div>'% str(uuid.uuid4())
            self.write( {'html':html,})

        self.new_messages(self.user, [cmd])
        #self.finish()


class MessageUpdatesHandler(BaseHandler, MessageMixin):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    def post(self):
        #registers itself as a callback with MessageMixin.wait_for_messages
        cursor = self.get_argument("cursor", None)
        self.wait_for_messages(self.async_callback(self.on_new_messages),
                               cursor=cursor)

    def on_new_messages(self, messages):
        # Closed client connection
        if self.request.connection.stream.closed():
            return

        msgs = []
        for msg in messages:
            if msg.startswith('!@#'):
                msgtype = 'board'
                msg = msg[3:]
            else:
                msgtype = 'default'
            #seems like the javascript only cares about the 'html'
            message = {
                "id": str(uuid.uuid4()),
                "from": self.user,
                "body": msg,
                "type": type,
                "html": '<div class="message" id="%s" >%s</div>'% (str(uuid.uuid4()), msg)
            }
            msgs.append( message)

        """
        if not self._finished:
            self.finish(dict(messages=msgs)) #turns into a json dict

        else:
            print 'finished'
            p = MessageMixin.players[ self.user]
            for m in messages:
                p.buffer.append( m)
        """
        self.finish(dict(messages=msgs)) #turns into a json dict
        


from templates import Login
import md5
class LoginHandler(BaseHandler):
    magic = 'ef47862869f311de943f001e4c8e3a11' # uh.. nothing to see here

    def get(self, errormsg=None):
        #send the generic login screen
        self.render( Login, errormsg=errormsg, xsrf=self.xsrf_token)

    def post(self):
        login = self.get_argument("login", None)
        password = self.get_argument("password", None)

        if not login and not password:
            errormsg = "please enter a name and a password"
            return self.get( errormsg)

        #make hash to compare
        password = md5.new(password+self.magic).hexdigest()
        user = M.noldb.players.find_one( {'login':login})

        if user:
            #check the password
            if password == user['passhash']: self._on_auth(login)
            else:
                return self.get( "password denied")

        else:
            #log new player
            M.noldb.players.insert( {'login':login, 'passhash':password})
            self._on_auth( login)

    def _on_auth(self, user):
        self.set_secure_cookie("user", tornado.escape.json_encode(user))
        self.redirect("/")


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.write("You are now logged out")

B = True

def main():


    #load the levels:
    from book import Book
    global B
    B = Book()
    Board = B.boards[0]


    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    print 'Booting on port 8888'
    main()
