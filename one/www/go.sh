PIDFILE=www.nolimyn.pid
python manage.py runfcgi socket=/tmp/helloworld.fcgi pidfile=$PIDFILE

