from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.template import RequestContext
from django.db.models import Max, Min, Avg, Count
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
    for match in Match.objects.all().order_by("-date", "-id"):
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

def stats2(request):
    """ Does all kind of statistical fun fact calculations.
    
    """
    
    ALL_P_RESULTS = PlayerResult.objects.select_related() # User several times
    
    def minmax(aggfunc, round_type):
        """ Returns min or max value for a round type"""
        field = "sum_"+round_type
        val = ALL_P_RESULTS.aggregate(aggfunc(field))[field+'__max']
        results = ALL_P_RESULTS.filter(**{field: val})
        first = results.order_by('match__date', 'match__id').select_related()[0]
        return {'sum': val, 'mid': first.match_id,
                'pid': first.player_id, 'pname': first.player.name}
        
    def gt0_avg(round_type):
        field = "sum_"+round_type
        result = ALL_P_RESULTS.filter(**{field+"__gt": 0}).aggregate(Avg(field))
        print result
        return round(result[field+'__avg'],1)
    
    def bot(amount, value_field):
        return top(amount, value_field, "")
    def top(amount, value_field_usage, total_prechar="-"):
        select_query = {'total': '('+value_field_usage+')'}
        results = ALL_P_RESULTS.extra(select=select_query).order_by(total_prechar+'total', 'match__date', 'match__id')
        top = []
        for i in range(min(results.count(), amount)):
            top.append({'sum': results[i].total, 'mid': results[i].match_id,
                        'pid': results[i].player_id, 'pname': results[i].player.name})
        return top
    
    results_totals = ALL_P_RESULTS.extra(select={'total': '(sum_spades + sum_queens + sum_solitaire_lines + sum_solitaire_cards + sum_pass - sum_grand - sum_trumph)'})
    total_avg = sum([r.total for r in results_totals])/results_totals.count()
    best_match_results = bot(3, "sum_spades + sum_queens + sum_solitaire_lines + sum_solitaire_cards + sum_pass - sum_grand - sum_trumph")
    worst_match_results = top(3, "sum_spades + sum_queens + sum_solitaire_lines + sum_solitaire_cards + sum_pass - sum_grand - sum_trumph")
    
    data = {'spades': {'worst': minmax(Max, 'spades'),
                       'average': gt0_avg("spades")},
            
            'queens': {'worst': minmax(Max, 'queens'),
                       'average': gt0_avg("queens")},
            
            'solitaire_lines': {'worst': minmax(Max, "solitaire_lines"),
                                'average': gt0_avg("solitaire_lines")},
            'solitaire_cards': {'worst': minmax(Max, "solitaire_cards"),
                                'average': gt0_avg("solitaire_cards")},
            'solitaire_total': {'worst': top(1, "sum_solitaire_lines + sum_solitaire_cards")[0]},
            
            'pass': {'worst': minmax(Max, 'pass')},
            
            'grand': {'best': minmax(Max, 'grand')},
            
            'trumph': {'best': minmax(Max, 'trumph')},
            
            'total': {'best': best_match_results[0],
                    'second': best_match_results[1],
                    'third': best_match_results[2],
                    'worst': worst_match_results[0],
                    'average': total_avg},
            }
    return render_to_response('stats.html', data, context_instance=RequestContext(request))

def rating(request):
    _update_ratings()
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