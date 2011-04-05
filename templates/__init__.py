from genshi.template import TemplateLoader
import os.path
loader = TemplateLoader( os.path.dirname(__file__))

Login = loader.load('login.html')
Main = loader.load('index.html')
Anonytemplate = loader.load('anonybot.html')
