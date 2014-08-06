# Create your views here.
from django.http import HttpResponse

def hello(req, url):
	return HttpResponse('Hey, world! I live at %s'%url )

from django.http import HttpResponse
from django.template import Context, loader
def fancyhello(req):
   t = loader.get_template('index.html')
   r = t.render( Context({'prev':False,}))
   return HttpResponse( r)

