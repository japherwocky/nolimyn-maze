from django.conf.urls.defaults import *
from views import hello, fancyhello

urlpatterns = patterns('',
    # Example:
    # (r'^helloworld/', include('helloworld.apps.foo.urls.foo')),
	# ('^helloworld/$', include('helloworld.urls')),

	('^orbitfoo', fancyhello),
	 ('(?P<url>.*)', hello ),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
