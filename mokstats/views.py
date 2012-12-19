from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.template import RequestContext
from django.db.models import Max, Min
from models import *
from rating import RatingCalculator, RatingResult, START_RATING
from django.core.cache import cache
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
import calendar, copy
import logging
logger = logging.getLogger("file_logger")

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
        _update_ratings()
        match_winners_cache = {}
        players = []
        for player in Player.objects.all():
            player_results = PlayerResult.objects.filter(player=player)
            player_result_ids = player_results.values_list('match_id', flat=True)
            matches = Match.objects.filter(id__in=player_result_ids, place_id__in=place_ids)
            # Played - Win Ratio
            won = 0
            for match in matches:
                winners = match_winners_cache.get(match.id, False)
                if not winners: # Not in cache
                    winners = match.get_winners()
                    match_winners_cache[match.id] = winners
                if player in winners:
                    won+=1
            played_count = matches.count()
            if played_count == 0:
                win_percent = 0
            else:
                win_percent = int(round(won*100.00/played_count))
            # Get last rating
            if player_results.exists():
                rating = int(player_results.order_by('-match__date', '-match__id')[0].rating)
            else:
                rating = "-"
            players.append({'id': player.id, 'name': player.name,
                            'played': played_count, 'won': won,
                            'win_perc': win_percent, 'rating': rating})
        cache.set(cache_string, players)
        
    places = []
    for place in Place.objects.all():
        p = {'name': place.name}
        p['selected'] = "selected" if (place.id in place_ids) else ""
        places.append(p)
    data = {'players': players, 'places': places}
    return render_to_response('players.html', data, context_instance=RequestContext(request))

def player(request, pid):
    _update_ratings()
    player = Player.objects.get(id=pid)
    player_result_ids = PlayerResult.objects.filter(player=player).values_list('match_id', flat=True)
    matches = Match.objects.filter(id__in=player_result_ids)
    # Won - Loss - Other counts
    won = 0
    lost = 0
    for match in matches:
        position = match.get_position(player.id)
        if position == 1:
            won += 1
        elif position == PlayerResult.objects.filter(match=match).count():
            lost += 1
    data = {'name': player.name, 'id': player.id, 'won': won, 'lost': lost, 
            'played': matches.count(), 'ratings': player.get_ratings()}
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
    _update_ratings()
    # Get match
    m = Match.objects.select_related('place').get(id=mid)
    results = []
    # Get players result for match
    for result in PlayerResult.objects.select_related('player', 'match__date').filter(match=m):
        vals = result.vals()
        if vals['player']['id'] in [p.id for p in m.get_winners()]:
            vals['winner'] = True
        else:
            vals['winner'] = False
        results.append(vals)
    # Sort matches by game position
    results = sorted(results, key=lambda result: result['total'])
    # Create context data and return http request
    data = {'year': m.date.year,
            'month': _month_name(m.date.month),
            'place': m.place.name,
            'results': results,
            'next_match_id': m.get_next_match_id(),
            'prev_match_id': m.get_prev_match_id()}
    return render_to_response('match.html', data, context_instance=RequestContext(request))

def stats(request):
    data = {'spades': {'best': {'sum': 100, 'pid': 0, 'pname': 'unknown'},
                      'worst': {'sum': -1, 'pid': 0, 'pname': 'unknown'},
                      'average': 0},
            'queens': {'best': {'sum': 100, 'pid': 0, 'pname': 'unknown'},
                      'worst': {'sum': -1, 'pid': 0, 'pname': 'unknown'},
                      'average': 0},
            'solitaire_lines': {'best': {'sum': 1000, 'pid': 0, 'pname': 'unknown'},
                                'worst': {'sum': -1, 'pid': 0, 'pname': 'unknown'},
                                'average': 0},
            'solitaire_cards': {'best': {'sum': 100, 'pid': 0, 'pname': 'unknown'},
                                'worst': {'sum': -1, 'pid': 0, 'pname': 'unknown'},
                                'average': 0},
            'solitaire_total': {'worst':{'sum': -1, 'pid': 0, 'pname': 'unknown', 'mid': 0}},
            'pass': {'best': {'sum': 100, 'pid': 0, 'pname': 'unknown'},
                     'worst': {'sum': -1, 'pid': 0, 'pname': 'unknown'},
                     'average': 0},
            'grand': {'best': {'sum': -1, 'pid': 0, 'pname': 'unknown'},
                      'worst': {'sum': 100, 'pid': 0, 'pname': 'unknown'},
                      'average': 0},
            'trumph': {'best': {'sum': -1, 'pid': 0, 'pname': 'unknown'},
                      'worst': {'sum': 100, 'pid': 0, 'pname': 'unknown'},
                      'average': 0},
            'total': {'best': {'sum': 1000, 'pid': 0, 'pname': 'unknown', 'mid': 0},
                    'second': {'sum': 1000, 'pid': 0, 'pname': 'unknown', 'mid': 0},
                    'third': {'sum': 1000, 'pid': 0, 'pname': 'unknown', 'mid': 0},
                    'worst': {'sum': -1000, 'pid': 0, 'pname': 'unknown', 'mid': 0},
                    'average': 0},
            }
    
    def compare(result, round_sum, round_type, stats_type, greater=True):
        """ Define a reusable method that compares round data with best/worst data
        @param result:     The PlayerResult object
        @param round_sum:  The sum to be compared with current sum
        @param round_type: Typical spades, queens, etc
        @param stats_type: Either best, or worst string
        @param greater:    If the sum has to be greater/lesser than current sum to be set.
        
        """
        current_sum = data[round_type][stats_type]['sum']
        #print "current %s, vs round %s, round %s, stats %s, greater %s" % (current_sum, round_sum, round_type, stats_type, greater)
        if (greater and (round_sum > current_sum)) or (not greater and (round_sum < current_sum)):
            data[round_type][stats_type]['sum'] = round_sum
            data[round_type][stats_type]['pid'] = result.player_id
            data[round_type][stats_type]['pname'] = result.player.name
            if data[round_type][stats_type].has_key("mid"):
                data[round_type][stats_type]['mid'] = result.match_id
    
    player_results = PlayerResult.objects.select_related('player').order_by('match__date')
    
    if player_results.count() == 0:
        return render_to_response('stats.html', data, context_instance=RequestContext(request))
    
    round_types = ['spades', 'queens', 'solitaire_lines', 'solitaire_cards', 'pass', 'grand', 'trumph']
    for result in player_results:
        for round_type in round_types:
            # Check if the game type is of the reversed type
            if round_type in ['grand', 'trumph']:
                best_worst = [True, False]
            else:
                best_worst = [False, True]
            # Get sum and average
            round_sum = eval('result.sum_'+round_type)
            if round_sum > 0:
                data[round_type]['average'] += round_sum
            # Compare and update data
            compare(result, round_sum, round_type, "best", best_worst[0])
            compare(result, round_sum, round_type, "worst", best_worst[1])
        #Solitaire total
        soli_total = result.sum_solitaire_lines + result.sum_solitaire_cards
        compare(result, soli_total, "solitaire_total", "worst", True)
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
            data['total']['best']['mid'] = result.match_id
        elif total < data['total']['second']['sum']:
            # Copy second best to third best
            data['total']['third'] = copy.copy(data['total']['second'])
            # Rewrite second best
            data['total']['second']['sum'] = total
            data['total']['second']['pid'] = result.player_id
            data['total']['second']['pname'] = result.player.name
            data['total']['second']['mid'] = result.match_id
        elif total < data['total']['third']['sum']:
            data['total']['third']['sum'] = total
            data['total']['third']['pid'] = result.player_id
            data['total']['third']['pname'] = result.player.name
            data['total']['third']['mid'] = result.match_id
        if total > data['total']['worst']['sum']:
            data['total']['worst']['sum'] = total
            data['total']['worst']['pid'] = result.player_id
            data['total']['worst']['pname'] = result.player.name
            data['total']['worst']['mid'] = result.match_id
    # Calculate averages
    for round_type in (round_types+['total']):
        data[round_type]['average'] /= player_results.count()
    return render_to_response('stats.html', data, context_instance=RequestContext(request))

def rating(request):
    if PlayerResult.objects.count() == 0:
        return render_to_response('rating.html', {}, context_instance=RequestContext(request))
    max_rating = PlayerResult.objects.aggregate(Max('rating'))['rating__max']
    max_obj = PlayerResult.objects.select_related('player__name').filter(rating = max_rating).order_by('match__date', 'match__id')[0]
    min_rating = PlayerResult.objects.aggregate(Min('rating'))['rating__min']
    min_obj = PlayerResult.objects.select_related('player__name').filter(rating = min_rating).order_by('match__date', 'match__id')[0]
    players = Player.objects.all()
    player_names = simplejson.dumps([p.name for p in players], cls=DjangoJSONEncoder)
    data = {'max': {'pid': max_obj.player_id, 'pname': max_obj.player.name, 
                    'mid': max_obj.match_id, 'rating': max_obj.rating},
            'min': {'pid': min_obj.player_id, 'pname': min_obj.player.name, 
                    'mid': min_obj.match_id, 'rating': min_obj.rating},
            'players': [p.get_ratings() for p in players],
            'player_names': player_names,
            }
    return render_to_response('rating.html', data, context_instance=RequestContext(request))

def _month_name(month_number):
    return calendar.month_name[month_number]

def _update_ratings():
    calc = RatingCalculator()
    players = {}
    match_ids = list(set(PlayerResult.objects.filter(rating=None).values_list('match_id', flat=True)))
    for match in Match.objects.filter(id__in=match_ids).order_by('date', 'id'):
        player_positions = match.get_positions()
        rating_results = []
        for p in player_positions:
            # Fetch the current rating value
            #if not players.get(p['id'], False):
                rated_results = PlayerResult.objects.filter(player=p['id']).exclude(rating=None).order_by('-match__date', '-match__id')
                if not rated_results.exists():
                    rating = START_RATING
                else:
                    rating = rated_results[0].rating
            #else:
            #    rating = players[p['id']]
                rating_results.append(RatingResult(p['id'], rating, p['position']))
        # Calculate new ratings
        new_player_ratings = calc.new_ratings(rating_results)
        # Update
        for p in new_player_ratings:
            players[p.dbid] = p.rating
            PlayerResult.objects.filter(player=p.dbid).filter(match=match).update(rating=p.rating)