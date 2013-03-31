import os
import sys

path = '/srv/djangoapps/mokstatsapp'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mokstats.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
