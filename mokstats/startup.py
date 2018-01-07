from django.apps import AppConfig
from django.core.management import call_command


class MokstatsConfig(AppConfig):
    name = 'mokstats'
    verbose_name = "Mokstats"

    def ready(self):
        print 'Mokstats startup script - START'

        print 'Creating cache table if it does not exist...'
        call_command('createcachetable')

        print 'Mokstats startup script - END'
