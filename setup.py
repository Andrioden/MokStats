#Simulates django shell environment
import sys; print('%s %s' % (sys.executable or sys.platform, sys.version))
from django.core import management;import mokstats.settings as settings;management.setup_environ(settings)

#Code
from mokstats.models import Configuration
if Configuration.objects.count() == 0:
    conf = Configuration()
    conf.save()
    print "Configuration created and saved"
else:
    print "An configuration already existed"

#Stops the window from closing so output can be read
print 'Click any key to close'
raw_input()