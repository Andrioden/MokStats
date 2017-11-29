from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

""" Hide some admin panel models """
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
admin.site.unregister(User)
admin.site.unregister(Group)

from mokstats import views, ajax

""" LIST OF PATTERNS """
urlpatterns = [
    url(r'^$', views.index),
    url(r'^players/(?P<pid>\d+)/$', views.player),
    url(r'^players/$', views.players),
    url(r'^matches/(?P<mid>\d+)/$', views.match),
    url(r'^matches/$', views.matches),
    url(r'^stats/$', views.stats),
    url(r'^stats/best-results/$', views.stats_best_results),
    url(r'^stats/worst-results/$', views.stats_worst_results),
    url(r'^stats/top-rounds/$', views.stats_top_rounds),
    url(r'^stats/biggest-match-sizes/$', views.stats_biggest_match_sizes),
    url(r'^rating/$', views.rating),
    url(r'^rating/description/$', views.rating_description),
    url(r'^activity/$', views.activity),
    # AJAX CALLS
    url(r'^ajax_last_playerlist/$', ajax.last_playerlist),
    # ADMIN PAGES
    url(r'^admin/', include(admin.site.urls)),
]

urlpatterns += staticfiles_urlpatterns()