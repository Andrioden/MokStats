from django.shortcuts import render_to_response
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.template import RequestContext
from models import *
from django.core.cache import cache

def index(request):
    return render_to_response('index.html', {}, context_instance=RequestContext(request))

def players(request):
    cached_data = cache.get('players')
    #cached_data = None
    if cached_data:
        data =  cached_data
        print 'FOUND IN CACHE'
    else:
        players = []
        for player in Player.objects.all():
            matches = Match.objects.filter(id__in=PlayerResult.objects.filter(player=player).values_list('match_id', flat=True))
            won = 0
            for match in matches:
                if player in match.get_winners():
                    won+=1
            players.append({'id': player.id, 'name': player.name, 'played': matches.count(), 'won': won, 'win_perc': won*100/matches.count()})
        data = {'players': players}
        cache.set('players', data)
        print 'CACHED'
    return render_to_response('players.html', data, context_instance=RequestContext(request))

def matches(request):
    data = {'matches': Match.objects.all().values()}
    return render_to_response('matches.html', data, context_instance=RequestContext(request))

def stats(request):
    return render_to_response('stats.html', {}, context_instance=RequestContext(request))