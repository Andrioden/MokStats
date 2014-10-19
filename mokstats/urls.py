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
    # VIEWS
    (r'^$', 'mokstats.views.index'),
    (r'^players/(?P<pid>\d+)/$', 'mokstats.views.player'),
    (r'^players/$', 'mokstats.views.players'),
    (r'^matches/(?P<mid>\d+)/$', 'mokstats.views.match'),
    (r'^matches/$', 'mokstats.views.matches'),
    (r'^stats/$', 'mokstats.views.stats'),
    (r'^stats/best-results/$', 'mokstats.views.stats_best_results'),
    (r'^stats/worst-results/$', 'mokstats.views.stats_worst_results'),
    (r'^stats/top-rounds/$', 'mokstats.views.stats_top_rounds'),
    (r'^stats/biggest-match-sizes/$', 'mokstats.views.stats_biggest_match_sizes'),
    (r'^rating/$', 'mokstats.views.rating'),
    (r'^rating/description/$', 'mokstats.views.rating_description'),
    (r'^activity/$', 'mokstats.views.activity'),
    (r'^system-status/$', 'mokstats.views.system_status'),
    # AJAX CALLS
    (r'^ajax_last_playerlist/$', 'mokstats.ajax.last_playerlist'),
    # ADMIN PAGES
    (r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()