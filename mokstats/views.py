from django.shortcuts import render_to_response, get_object_or_404
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.template import RequestContext
from models import *
from django.core.cache import cache
import calendar, copy

def index(request):
    return render_to_response('index.html', {}, context_instance=RequestContext(request))

def players(request):
    places_strings = request.GET.getlist('places[]', None)

    # Validate that all places exists
    place_ids = []
    for place in places_strings:
        place_ids.append(get_object_or_404(Place, name=place).id)
    if not place_ids:
        place_ids = Place.objects.values_list('id', flat=True)
    place_ids = sorted(place_ids)

    # Make valid cache string
    cache_string = "players_places"
    for pid in place_ids:
        cache_string += str(pid)
        if not pid == place_ids[-1]: # Not last item
            cache_string += ","
            
    # Get stats data, either from cache or from database
    cached_players = cache.get(cache_string)
    if cached_players:
        players =  cached_players
    else:
        players = []
        for player in Player.objects.all():
            player_result_ids = PlayerResult.objects.filter(player=player).values_list('match_id', flat=True)
            matches = Match.objects.filter(id__in=player_result_ids, place_id__in=place_ids)
            won = 0
            for match in matches:
                if player in match.get_winners():
                    won+=1
            played_count = matches.count()
            if played_count == 0:
                win_percent = 0
            else:
                win_percent = int(round(won*100.00/played_count))
            players.append({'id': player.id, 'name': player.name, 'played': played_count, 'won': won, 'win_perc': win_percent})
        cache.set(cache_string, players)
        
    places = []
    for place in Place.objects.all():
        p = {'name': place.name}
        p['selected'] = "selected" if (place.id in place_ids) else ""
        places.append(p)
    data = {'players': players, 'places': places}
    return render_to_response('players.html', data, context_instance=RequestContext(request))

def player(request, pid):
    player = Player.objects.get(id=pid)
    player_result_ids = PlayerResult.objects.filter(player=player).values_list('match_id', flat=True)
    matches = Match.objects.filter(id__in=player_result_ids)
    won = 0
    lost = 0
    for match in matches:
        position = match.get_position(player.id)
        if position == 1:
            won += 1
        elif position == PlayerResult.objects.filter(match=match).count():
            lost += 1
    data = {'name': player.name, 'won': won, 'lost': lost, 'played': matches.count()}
    return render_to_response('player.html', data, context_instance=RequestContext(request))

def matches(request):
    places = {}
    for place in Place.objects.all():
        places[place.id] = place.name
    matches = []
    for match in reversed(Match.objects.all()):
        matches.append({'id': match.id,
                        'year': match.date.year, 
                        'month': _month_name(match.date.month),
                        'place': places[match.place_id]})
    data = {'matches': matches}
    return render_to_response('matches.html', data, context_instance=RequestContext(request))

def match(request, mid):
    # Get match
    m = Match.objects.select_related('place').get(id=mid)
    results = []
    # Get players result for match
    for result in PlayerResult.objects.select_related('player').filter(match=m):
        vals = result.vals()
        if vals['player']['id'] in [p.id for p in m.get_winners()]:
            vals['winner'] = True
        else:
            vals['winner'] = False
        results.append(vals)
    # Sort matches by game position
    results = sorted(results, key=lambda result: result['total'])
    # Create context data and return http request
    match = {'year': m.date.year,
             'month': _month_name(m.date.month),
             'place': m.place.name,
             'results': results}
    return render_to_response('match.html', match, context_instance=RequestContext(request))

def stats(request):
    data = {'spades': {'best': {'sum': 100, 'pid': 0, 'pname': 'unknown'},
                      'worst': {'sum': -100, 'pid': 0, 'pname': 'unknown'},
                      'average': 0},
            'queens': {'best': {'sum': 100, 'pid': 0, 'pname': 'unknown'},
                      'worst': {'sum': -100, 'pid': 0, 'pname': 'unknown'},
                      'average': 0},
            'solitaire_lines': {'best': {'sum': 1000, 'pid': 0, 'pname': 'unknown'},
                      'worst': {'sum': -1, 'pid': 0, 'pname': 'unknown'},
                      'average': 0},
            'solitaire_cards': {'best': {'sum': 100, 'pid': 0, 'pname': 'unknown'},
                      'worst': {'sum': -1, 'pid': 0, 'pname': 'unknown'},
                      'average': 0},
            'solitaire_total': {'worst':{'sum': -1, 'pid': 0, 'pname': 'unknown'}},
            'pass': {'best': {'sum': 100, 'pid': 0, 'pname': 'unknown'},
                     'worst': {'sum': -100, 'pid': 0, 'pname': 'unknown'},
                     'average': 0},
            'grand': {'best': {'sum': 100, 'pid': 0, 'pname': 'unknown'},
                      'worst': {'sum': -100, 'pid': 0, 'pname': 'unknown'},
                      'average': 0},
            'trumph': {'best': {'sum': 100, 'pid': 0, 'pname': 'unknown'},
                      'worst': {'sum': -100, 'pid': 0, 'pname': 'unknown'},
                      'average': 0},
            'total': {'best': {'sum': 1000, 'pid': 0, 'pname': 'unknown'},
                    'second': {'sum': 1000, 'pid': 0, 'pname': 'unknown'},
                    'third': {'sum': 1000, 'pid': 0, 'pname': 'unknown'},
                    'worst': {'sum': -1000, 'pid': 0, 'pname': 'unknown'},
                    'average': 0},
            }
    
    #TODO: Add all other types
    player_results = PlayerResult.objects.select_related('player').order_by('match__date').all()
    round_types = ['spades', 'queens', 'solitaire_lines', 'solitaire_cards', 'pass', 'grand', 'trumph']
    for result in player_results:
        for round_type in round_types:
            round_sum = eval('result.sum_'+round_type)
            if round_sum > 0:
                data[round_type]['average'] += round_sum
            if result.sum_spades < data[round_type]['best']['sum']:
                data[round_type]['best']['sum'] = round_sum
                data[round_type]['best']['pid'] = result.player_id
                data[round_type]['best']['pname'] = result.player.name
            if result.sum_spades > data[round_type]['worst']['sum']:
                data[round_type]['worst']['sum'] = round_sum
                data[round_type]['worst']['pid'] = result.player_id
                data[round_type]['worst']['pname'] = result.player.name
        #Solitaire total
        soli_total = result.sum_solitaire_lines + result.sum_solitaire_cards
        if soli_total > data['solitaire_total']['worst']['sum']:
            data['solitaire_total']['worst']['sum'] = soli_total
            data['solitaire_total']['worst']['pid'] = result.player_id
            data['solitaire_total']['worst']['pname'] = result.player.name
        #Sum
        total = result.total()
        data['total']['average'] += total
        if total < data['total']['best']['sum']:
            # Copy second best to third best
            data['total']['third'] = copy.copy(data['total']['second'])
            # Copy best to second best
            data['total']['second'] = copy.copy(data['total']['best'])
            # Rewrite best
            data['total']['best']['sum'] = total
            data['total']['best']['pid'] = result.player_id
            data['total']['best']['pname'] = result.player.name
        elif total < data['total']['second']['sum']:
            # Copy second best to third best
            data['total']['third'] = copy.copy(data['total']['second'])
            # Rewrite second best
            data['total']['second']['sum'] = total
            data['total']['second']['pid'] = result.player_id
            data['total']['second']['pname'] = result.player.name
        elif total < data['total']['third']['sum']:
            data['total']['third']['sum'] = total
            data['total']['third']['pid'] = result.player_id
            data['total']['third']['pname'] = result.player.name
        if total > data['total']['worst']['sum']:
            data['total']['worst']['sum'] = total
            data['total']['worst']['pid'] = result.player_id
            data['total']['worst']['pname'] = result.player.name
    # Calculate averages
    for round_type in (round_types+['total']):
        data[round_type]['average'] /= player_results.count()
            
    
    return render_to_response('stats.html', data, context_instance=RequestContext(request))


def _month_name(month_number):
    return calendar.month_name[month_number]