#!/usr/bin/env python

import logging
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import os.path
import uuid

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

from telnetlib import Telnet
class MudHandler:
	commands = []
	_running = False
	"""
	Read from the MUD, passing through a handler, proc, which should
	expect a string argument and return None or a string to be sent (w/o \n)
	"""
	def __init__(self, host, port, proc=False):
		self.t = Telnet()
		self.t.open(host,port)
		if proc: self.proc = proc
		print 'initd, proc:%s' % proc

	def __call__(self):
		try:
			self.write( self.proc( self.t.read_very_eager()))
			#send user's commands
			if MudHandler.commands:
				cmds = MudHandler.commands
				[self.write( cmd) for cmd in cmds[:13] ]
				print cmds
				cmds = cmds[12:]
				print cmds
				MudHandler.commands = cmds
			tornado.ioloop.IOLoop.instance().add_callback( self )
		except EOFError:			
			MessageMixin.new_messages( [ self.render({'id':str(uuid.uuid4()), 'from':'', 'body':'Disconnected'})])
			MudHandler._running = False
		except Exception, e:
			raise

	def write(self, instring):
		if instring:
			#import pdb;pdb.set_trace()
			instring = str( instring)
			self.t.write( instring + '\n' )	

	def proc(self, text):
		if text:
			msgs = [ {'id':str(uuid.uuid4()), 'from':' ', 'body':line} for line in text.split('\n') ]
			if msgs:
				msgs = [ self.render(msg) for msg in msgs]
				MessageMixin.new_messages( msgs)

	def render(self, msg):
		msg['html'] = '<div class="message" id="%s"><pre>%s</pre></div>\n' % ( msg['id'], msg['body'])
		return msg
		
		
		
class Application(tornado.web.Application):
	def __init__(self):

		handlers = [
			(r"/", MainHandler),
			(r"/auth/login", AuthLoginHandler),
			(r"/auth/logout", AuthLogoutHandler),
			(r"/a/message/new", MessageNewHandler),
			(r"/a/message/updates", MessageUpdatesHandler),
		]
		settings = dict(
			cookie_secret="43oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
			login_url="/auth/login",
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


class MainHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self):

		message = {
			"id": str(uuid.uuid4()),
			"from": '',
			"body": "Welcome %s, to AnonyBot." % self.current_user["first_name"],
		}

		"""	
		def foo(): 
			msg = {"id": str(uuid.uuid4()), "from": 'BOTBOT', "body": str(uuid.uuid4())}
			msg['html'] = '<div class="message" id="m{{ message["id"] }}"><b>{{ escape(message["from"]) }}: </b>{{ escape(message["body"]) }}</div>'
			MessageMixin.new_messages([msg])
			#import time; time.sleep(12)
		goo = tornado.ioloop.DelayedCallback( foo, 2000, tornado.ioloop.IOLoop.instance() )
		goo.start()
		#tornado.ioloop.IOLoop.instance().add_callback( ghetto )
		"""

		message["html"] = self.render_string("message.html", message=message)

		if not MudHandler._running:
			M = MudHandler( 'pearachute.net', 9998)
			tornado.ioloop.IOLoop.instance().add_callback( M )
			MudHandler._running = True

		MessageMixin.new_messages([message])
		self.render("index.html", messages=MessageMixin.cache)


class MessageMixin(object):
	"""
	
	"""
	waiters = []
	cache = []
	cache_size = 200

	def wait_for_messages(self, callback, cursor=None):
		"""
		instead of a callback, we could pass a Player pointer..

		this looks in a giant pool of "every message ever"

		let's store messages in a {} of player ids.  instead of a cursor, we'll append to
		a list.. give callback a pointer to the {}, it can look for messages and send, or
		return False if it was empty: at which point we add it to a {} of waiters (so in
		new_messages, we can do foo in {})
		"""
		cls = MessageMixin
		if cursor: #check for messages that happened while we were sending the last batch
			index = 0
			for i in xrange(len(cls.cache)):
				index = len(cls.cache) - i - 1
				if cls.cache[index]["id"] == cursor: break
			recent = cls.cache[index + 1:]

			#if so, send'em!
			if recent:
				callback(recent)
				return
		cls.waiters.append(callback)

	@classmethod
	def new_messages(self, messages):
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
I don't see why these two classes couldn't be the same thing, esp.
since we don't need to pass a cursor arg.  POST for messages, GET for polling?
"""

class MessageNewHandler(BaseHandler, MessageMixin):
	@tornado.web.authenticated
	def post(self):
		message = {
			"id": str(uuid.uuid4()),
			"from": self.current_user["first_name"],
			"body": self.get_argument("body"),
		}
		message["html"] = self.render_string("message.html", message=message)
		if self.get_argument("next", None):
			self.redirect(self.get_argument("next"))
		else:
			self.write(message)
		self.new_messages([message])
		print 'in: %s' % message['body']
		MudHandler.commands.append( message['body'])


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
		self.finish(dict(messages=messages))


class AuthLoginHandler(BaseHandler, tornado.auth.GoogleMixin):
	@tornado.web.asynchronous
	def get(self):
		if self.get_argument("openid.mode", None):
			self.get_authenticated_user(self.async_callback(self._on_auth))
			return
		self.authenticate_redirect(ax_attrs=["name"])
	
	def _on_auth(self, user):
		"""
		Need to check for new users, instantiate, insert Player() / Body() classes..
		"""
		if not user:
			raise tornado.web.HTTPError(500, "Google auth failed")
		self.set_secure_cookie("user", tornado.escape.json_encode(user))
		self.redirect("/")



class AuthLogoutHandler(BaseHandler):
	def get(self):
		"""
		This is kind of silly, because the GOOG cookie stays set, and
		if they return, they get redirected real quick and stay logged
		in anyhow
		"""
		self.clear_cookie("user")
		self.write("You are now logged out")


def main():

	#instantiate a Board() here, pass it to Application()

	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
	main()
