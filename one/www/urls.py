from django.conf.urls.defaults import *
from hello.views import hello, fancyhello

urlpatterns = patterns('',
    # Example:
	 #(r'^helloworld.fcgi/', include('helloworld.urls')),
    (r'helloworld/orbitfoo/', fancyhello),
	 (r'(.*)', hello),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
