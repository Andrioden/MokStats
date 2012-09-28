from django.shortcuts import render_to_response
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.template import RequestContext
from models import *
from django.core.cache import cache
import calendar

def index(request):
    return render_to_response('index.html', {}, context_instance=RequestContext(request))

def players(request):
    cached_data = cache.get('players')
    if cached_data:
        data =  cached_data
    else:
        players = []
        for player in Player.objects.all():
            matches = Match.objects.filter(id__in=PlayerResult.objects.filter(player=player).values_list('match_id', flat=True))
            won = 0
            for match in matches:
                if player in match.get_winners():
                    won+=1
            played_count = matches.count()
            if played_count == 0:
                win_percent = 0
            else:
                win_percent = won*100/played_count
            players.append({'id': player.id, 'name': player.name, 'played': played_count, 'won': won, 'win_perc': win_percent})
        data = {'players': players}
        cache.set('players', data)
    return render_to_response('players.html', data, context_instance=RequestContext(request))

def matches(request):
    print "oklol"
    places = {}
    for place in Place.objects.all():
        places[place.id] = place.name
    matches = []
    for match in Match.objects.all():
        matches.append({'id': match.id,
                        'year': match.date.year, 
                        'month': _month_name(match.date.month),
                        'place': places[match.place_id]})
    data = {'matches': matches}
    return render_to_response('matches.html', data, context_instance=RequestContext(request))

def match(request, mid):
    print "lol"
    print mid
    # Get match
    m = Match.objects.select_related('place').get(id=mid)
    print m
    results = []
    # Get players result for match
    print "sec"
    for result in PlayerResult.objects.select_related('player').filter(match=m):
        print "here"
        vals = result.vals()
        if vals['player']['id'] in [p.id for p in m.get_winners()]:
            vals['winner'] = True
        else:
            vals['winner'] = False
        results.append(vals)
    print "now"
    # Sort matches by game position
    results = sorted(results, key=lambda result: result['total'])
    # Create context data and return http request
    match = {'year': m.date.year,
             'month': _month_name(m.date.month),
             'place': m.place.name,
             'results': results}
    return render_to_response('match.html', match, context_instance=RequestContext(request))

def stats(request):
    return render_to_response('stats.html', {}, context_instance=RequestContext(request))


def _month_name(month_number):
    return calendar.month_name[month_number]