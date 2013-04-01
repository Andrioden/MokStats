import sys, os

# Add project directory to path
sys.path.insert(0,os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2]))

# Connect Django to WSGI
os.environ['DJANGO_SETTINGS_MODULE'] = 'mokstats.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()