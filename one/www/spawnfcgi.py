#!/usr/bin/python
import sys, os

# Add a custom Python path.
sys.path.insert(0, "/lib/src/flup-1.0.1/")
sys.path.insert(0, "/var/www/")

# Switch to the directory of your project. (Optional.)
os.chdir("/var/nolimyn/www/")

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")

