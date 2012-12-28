import mokstats.models
from mokstats.models import Configuration
from django.db.models.signals import post_syncdb

""" This signal is run whenever the mokstats app is installed, not at every syncdb"""
def init_config(sender, **kwargs):
    if Configuration.objects.count() == 0:
        conf = Configuration()
        conf.save()
    pass
post_syncdb.connect(init_config, sender=mokstats.models)