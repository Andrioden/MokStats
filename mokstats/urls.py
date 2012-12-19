from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

""" Hide some admin panel models """
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
admin.site.unregister(User)
admin.site.unregister(Group)

""" LIST OF PATTERNS """
urlpatterns = patterns('',
    (r'^$', 'mokstats.views.index'),
    (r'^players/(?P<pid>\d+)/$', 'mokstats.views.player'),
    (r'^players/$', 'mokstats.views.players'),
    (r'^matches/(?P<mid>\d+)/$', 'mokstats.views.match'),
    (r'^matches/$', 'mokstats.views.matches'),
    (r'^stats/$', 'mokstats.views.stats2'),
    (r'^rating/$', 'mokstats.views.rating'),
    (r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()