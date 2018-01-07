# -*- coding: utf-8 -*-

from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext
from django.db.models import Max, Min, Avg, Count
from models import Place, Player, PlayerResult, Match, cur_config
from rating import RatingCalculator, RatingResult
import calendar
import os
import json
from operator import itemgetter


def index(request):
    return render(request, 'index.html', {})


def players(request):
    places_strings = request.GET.getlist('places[]', None)

    # Validate that all places exists
    place_ids = []
    for place in places_strings:
        place_ids.append(get_object_or_404(Place, name=place).id)
    if not place_ids:
        place_ids = Place.objects.values_list('id', flat=True)
    place_ids = sorted(place_ids)

    # Create stats
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
            if not winners:  # Not in cache
                winners = match.get_winners()
                match_winners_cache[match.id] = winners
            if player in winners:
                won += 1
        played_count = matches.count()
        if played_count == 0:
            win_percent = 0
        else:
            win_percent = int(round(won * 100.00 / played_count))
        # Get last rating
        if player_results.exists():
            rating = int(player_results.order_by('-match__date', '-match__id')[0].rating)
        else:
            rating = "-"
        players.append({'id': player.id, 'name': player.name,
                        'played': played_count, 'won': won,
                        'win_perc': win_percent, 'rating': rating})

    places = []
    for place in Place.objects.all():
        p = {'name': place.name}
        p['selected'] = "selected" if (place.id in place_ids) else ""
        places.append(p)
    data = {'players': players, 'places': places, 'config': {'active_treshold': cur_config().active_player_match_treshold}}

    return render(request, 'players.html', data)


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
    # Round performance
    all_calc = PlayerResultStatser(PlayerResult.objects.all())
    player_calc = PlayerResultStatser(PlayerResult.objects.filter(player=player))
    round_perf = []
    for round_type in ["spades", "queens", "solitaire", "pass", "grand", "trumph"]:
        if round_type == "solitaire":
            all_avg = all_calc.avg("sum_solitaire_lines + sum_solitaire_cards")
            player_avg = player_calc.avg("sum_solitaire_lines + sum_solitaire_cards")
        else:
            all_avg = all_calc.avg("sum_" + round_type)
            player_avg = player_calc.avg("sum_" + round_type)
        if round_type in ["grand", "trumph"]:
            good_average = player_avg >= all_avg
        else:
            good_average = player_avg < all_avg
        round_perf.append({
            'name': round_type.capitalize(),
            'type': round_type,
            'all_average': all_avg,
            'player_average': player_avg,
            'performance': round((player_avg - all_avg) * 100 / all_avg, 1),
            'good': good_average
        })
    data = {'name': player.name, 'id': player.id, 'won': won, 'lost': lost,
            'played': matches.count(), 'ratings': player.get_ratings(),
            'round_performances': round_perf}
    return render(request, 'player.html', data)


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
    return render(request, 'matches.html', data)


def match(request, mid):
    _update_ratings()
    # Get match
    m = Match.objects.select_related('place').get(id=mid)
    results = []
    # Get players result for match
    for result in PlayerResult.objects.select_related('player', 'match').filter(match=m):
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
            'day': m.date.day,
            'place': m.place.name,
            'results': results,
            'next_match_id': m.get_next_match_id(),
            'prev_match_id': m.get_prev_match_id(),
            'moffa_los': results[len(results) - 1]['player']['name'] == "Bengt",
            'moffa_win': (results[0]['player']['name'] == "Bengt") and (results[0]['total'] < 0),
            'aase_los': results[len(results) - 1]['player']['name'] == "Aase",
            'andre_win': results[0]['player']['name'] == u"André"}
    return render(request, 'match.html', data)


def stats(request):
    """ This is the stats page that show all the stats that didnt fit
    anywhere else.
    
    """
    ALL_RESULTS = PlayerResult.objects.select_related()
    PRS = PlayerResultStatser(ALL_RESULTS)

    # results_totals = ALL_RESULTS.extra(select={'total': '(sum_spades + sum_queens + sum_solitaire_lines + sum_solitaire_cards + sum_pass - sum_grand - sum_trumph)'})
    total_avg = round(sum([(r.sum_spades + r.sum_queens + r.sum_solitaire_lines + r.sum_solitaire_cards + r.sum_pass - r.sum_grand - r.sum_trumph) for r in ALL_RESULTS]) / (ALL_RESULTS.count() * 1.0), 1)

    best_match_result = PRS.bot_total(1)[0]
    worst_match_result = PRS.top_total(1)[0]

    trumph_stats = TrumphStatser(ALL_RESULTS)
    match_count = Match.objects.count()

    data = {'spades': {'worst': PRS.minmax(Max, 'spades'),
                       'gt0_average': PRS.gt0_avg("spades")},

            'queens': {'worst': PRS.minmax(Max, 'queens'),
                       'gt0_average': PRS.gt0_avg("queens")},

            'solitaire_lines': {'worst': PRS.minmax(Max, "solitaire_lines"),
                                'gt0_average': PRS.gt0_avg("solitaire_lines")},
            'solitaire_cards': {'worst': PRS.minmax(Max, "solitaire_cards"),
                                'gt0_average': PRS.gt0_avg("solitaire_cards")},
            'solitaire_total': {'worst': PRS.top(1, ["sum_solitaire_lines", "sum_solitaire_cards"])[0],
                                'average': PRS.avg("sum_solitaire_lines + sum_solitaire_cards")},

            'pass': {'worst': PRS.minmax(Max, 'pass')},

            'grand': {'best': PRS.minmax(Max, 'grand')},

            'trumph': {'best': PRS.minmax(Max, 'trumph'),
                       'average': PRS.avg("sum_trumph"),
                       'average_for_trumph_picker': round(trumph_stats.average_trumph_sum_for_trumph_pickers, 1),
                       'saved_count': trumph_stats.matches_trumph_picker_not_lost,
                       'saved_percent': round(trumph_stats.matches_trumph_picker_not_lost * 100 / float(match_count), 1)},

            'extremes': {'gain': PRS.top(1, ["sum_spades", "sum_queens", "sum_solitaire_lines", "sum_solitaire_cards", "sum_pass"])[0],
                         'loss': PRS.bot(1, ["-sum_grand", "-sum_trumph"])[0],
                         'match_size': Match.objects.annotate(count=Count("playerresult")).order_by("-count", "date", "id").values("id", "count")[0]},

            'total': {'best': best_match_result,
                      'worst': worst_match_result,
                      'gt0_average': total_avg},

            'match_count': match_count
            }
    return render(request, 'stats.html', data)


def stats_best_results(request):
    amount = int(request.GET.get("amount", 20))
    PRS = PlayerResultStatser(PlayerResult.objects.select_related())
    data = {'results': PRS.bot_total(amount), 'title': "%s beste kampresultater" % amount}
    return render(request, 'stats-result-list.html', data)


def stats_worst_results(request):
    amount = int(request.GET.get("amount", 20))
    PRS = PlayerResultStatser(PlayerResult.objects.select_related())
    data = {'results': PRS.top_total(amount), 'title': "%s dårligste kampresultater" % amount}
    return render(request, 'stats-result-list.html', data)


def stats_top_rounds(request):
    """ Page that show the best results for a specific round type """
    amount = int(request.GET.get("amount", 20))
    round_type = request.GET.get("round", None)
    if round_type == "solitaire":
        round_value_fields = ["sum_solitaire_lines", "sum_solitaire_cards"]
    else:
        round_value_fields = ["sum_%s" % round_type]
    PRS = PlayerResultStatser(PlayerResult.objects.select_related())
    data = {'results': PRS.top(amount, round_value_fields),
            'title': "%s toppresultater for %s " % (amount, round_type)}
    return render(request, 'stats-result-list.html', data)


def stats_biggest_match_sizes(request):
    match_amount = int(request.GET.get("amount", 20))
    biggest_matches = Match.objects.annotate(count=Count("playerresult")).order_by("-count", "date", "id").values("id", "count", "place__name", "date")
    data = {'matches': []}
    for match in biggest_matches[:match_amount]:
        data['matches'].append({
            'mid': match['id'],
            'size': match['count'],
            'place': match['place__name'],
            'year': match['date'].year,
            'month': _month_name(match['date'].month),
            # 'day': match['date'].day,
        })
    return render(request, 'stats-biggest-match-sizes.html', data)


def rating(request):
    _update_ratings()
    if PlayerResult.objects.count() == 0:
        return render_to_response('rating.html', {}, context_instance=RequestContext(request))
    max_rating = PlayerResult.objects.aggregate(Max('rating'))['rating__max']
    max_obj = PlayerResult.objects.select_related('player').filter(rating=max_rating).order_by('match__date', 'match__id')[0]
    min_rating = PlayerResult.objects.aggregate(Min('rating'))['rating__min']
    min_obj = PlayerResult.objects.select_related('player').filter(rating=min_rating).order_by('match__date', 'match__id')[0]
    # Only list active players
    active_players = []
    players = Player.objects.all()
    active_player_match_treshold = cur_config().active_player_match_treshold
    for p in players:
        if PlayerResult.objects.filter(player_id=p.id).count() >= active_player_match_treshold:
            active_players.append(p)
    # Create data context and return response
    data = {'max': {'pid': max_obj.player_id, 'pname': max_obj.player.name,
                    'mid': max_obj.match_id, 'rating': max_obj.rating},
            'min': {'pid': min_obj.player_id, 'pname': min_obj.player.name,
                    'mid': min_obj.match_id, 'rating': min_obj.rating},
            'players': [p.get_ratings() for p in active_players],
            'player_names': [p.name for p in active_players],
            }
    return render(request, 'rating.html', data)


def rating_description(request):
    conf = cur_config()
    data = {'K_VALUE': int(conf.rating_k),
            'START_RATING': int(conf.rating_start)}
    return render(request, 'rating-description.html', data)


def activity(request):
    matches = Match.objects.select_related('place').order_by('date')

    # First do a temporarly dynamic count that spawns from the start to the end
    data = {}
    first_year = matches[0].date.year
    last_year = matches[len(matches) - 1].date.year
    for match in matches:
        place = match.place.name
        if not data.has_key(place):
            data[place] = {}
            for year in range(first_year, last_year + 1):
                data[place][year] = {}
                for month in range(1, 13):
                    data[place][year][month] = 0
        # Add data
        data[place][match.date.year][match.date.month] += 1

    # use temporarly data to create fitting array for the template grapher
    response_places = []
    response_activities = []
    for place in data:
        place_activity = []
        for year in data[place]:
            for month in data[place][year]:
                c = data[place][year][month]
                if month < 10:
                    month = "0%s" % month
                place_activity.append(["%s-%s-15" % (year, month), c])
        response_places.append(place)
        response_activities.append(place_activity)

    response_data_jsonified = {'places': json.dumps(response_places), 'activity': json.dumps(response_activities)}
    return render(request, 'activity.html', response_data_jsonified)


def _month_name(month_number):
    return calendar.month_name[month_number]


def _update_ratings():
    calc = RatingCalculator()
    START_RATING = cur_config().rating_start
    players = {}
    match_ids = list(set(PlayerResult.objects.filter(rating=None).values_list('match_id', flat=True)))
    for match in Match.objects.filter(id__in=match_ids).order_by('date', 'id'):
        player_positions = match.get_positions()
        rating_results = []
        for p in player_positions:
            # Fetch the current rating value
            rated_results = PlayerResult.objects.filter(player=p['id']).exclude(rating=None).order_by('-match__date', '-match__id')
            if not rated_results.exists():
                rating = START_RATING
            else:
                rating = rated_results[0].rating
            rating_results.append(RatingResult(p['id'], rating, p['position']))
        # Calculate new ratings
        new_player_ratings = calc.new_ratings(rating_results)
        # Update
        for p in new_player_ratings:
            players[p.dbid] = p.rating
            PlayerResult.objects.filter(player=p.dbid).filter(match=match).update(rating=p.rating)


class PlayerResultStatser:
    """ Does all kind of statistical fun fact calculations with the
    supplied PlayerResult object.
    
    """
    ALL_RESULTS = None

    def __init__(self, all_results):
        self.ALL_RESULTS = all_results

    def minmax(self, aggfunc, round_type):
        """ Returns min or max value for a round type"""
        field = "sum_" + round_type
        val = self.ALL_RESULTS.aggregate(aggfunc(field))[field + '__max']
        results = self.ALL_RESULTS.filter(**{field: val})
        first = results.order_by('match__date', 'match__id').select_related()[0]
        return {'sum': val, 'mid': first.match_id,
                'pid': first.player_id, 'pname': first.player.name}

    def avg(self, value_field_usage):
        select_query = {'total': '(' + value_field_usage + ')'}
        average = 0.0
        for res in self.ALL_RESULTS.extra(select=select_query):
            average += res.total
        return round(average / self.ALL_RESULTS.count(), 1)

    def gt0_avg(self, round_type):
        """ Average score for the round type for results with greater than 0. """
        field = "sum_" + round_type
        result = self.ALL_RESULTS.filter(**{field + "__gt": 0}).aggregate(Avg(field))
        return round(result[field + '__avg'], 1)

    def top_total(self, amount):
        return self.top(amount, ["sum_spades", "sum_queens", "sum_solitaire_lines", "sum_solitaire_cards", "sum_pass", "-sum_grand", "-sum_trumph"])

    def bot_total(self, amount):
        return self.bot(amount, ["sum_spades", "sum_queens", "sum_solitaire_lines", "sum_solitaire_cards", "sum_pass", "-sum_grand", "-sum_trumph"])

    def bot(self, max_results, fields):
        return self.top(max_results, fields, False)

    def top(self, max_results, fields, reverse=True):
        """
        fields should be in the following format with a prefix that indicates if it is added or subtracted to the sum used to determine if its sort value:
        [
            "[prefix]<fieldname>",
        ]

        Example:
        [
            "sum_spades",
            "-sum_queens"
        ]

        """

        summarized_results = []
        for result in self.ALL_RESULTS:
            sum = 0
            for field in fields:
                field_multiplicator = 1
                if field[0] == '-':
                    field = field[1:]
                    field_multiplicator = -1
                sum += getattr(result, field) * field_multiplicator

            summarized_results.append({
                'sum': sum,
                'mid': result.match_id,
                'pid': result.player_id,
                'pname': result.player.name
            })

        return sorted(summarized_results, key=itemgetter('sum'), reverse=reverse)[:max_results]


class TrumphStatser:
    ALL_RESULTS = None

    average_trumph_sum_for_trumph_pickers = None
    matches_trumph_picker_not_lost = 0

    def __init__(self, all_results):
        self.ALL_RESULTS = all_results
        self.set_trumph_stats()

    def set_trumph_stats(self):
        match_sorted_results = {}
        for res in self.ALL_RESULTS.order_by('match'):
            if not match_sorted_results.has_key(res.match_id):
                match_sorted_results[res.match_id] = []
            match_sorted_results[res.match_id].append(res)

        trump_sum_for_trumph_pickers = []
        for match_results in match_sorted_results.itervalues():
            trumph_picker_player_result = self.get_trumph_picker_result_from_match_results(match_results)

            if trumph_picker_player_result == "IGNORE":
                continue
            else:
                # Average trumph picker sum list
                trump_sum_for_trumph_pickers.append(trumph_picker_player_result.sum_trumph)
                # Check if trumph picker avoided loss due to trumph pick
                match_loser_id = self.get_match_loser_id_from_match_results(match_results)
                if (match_loser_id == "IGNORE"):
                    pass
                elif trumph_picker_player_result.player_id != match_loser_id:
                    self.matches_trumph_picker_not_lost += 1

        self.average_trumph_sum_for_trumph_pickers = sum(trump_sum_for_trumph_pickers) / float(len(trump_sum_for_trumph_pickers))

    def get_trumph_picker_result_from_match_results(self, match_results):
        highest_sum_before_trumph = -1000
        has_multiple_trumphers = False
        trumph_picker_player_result = None

        for res in match_results:
            total_before_trumph = res.total_before_trumph()
            if total_before_trumph > highest_sum_before_trumph:
                highest_sum_before_trumph = total_before_trumph
                trumph_picker_player_result = res
                has_multiple_trumphers = False
            elif total_before_trumph == highest_sum_before_trumph:
                has_multiple_trumphers = True

        if has_multiple_trumphers:
            return "IGNORE"
        else:
            return trumph_picker_player_result

    def get_match_loser_id_from_match_results(self, match_results):
        highest_total_sum = -1000
        has_multiple_losers = False
        highest_player_result = None

        for res in match_results:
            total = res.total()
            if total > highest_total_sum:
                highest_total_sum = total
                highest_player_result = res
                has_multiple_losers = False
            elif total == highest_total_sum:
                has_multiple_losers = True

        if has_multiple_losers:
            return "IGNORE"
        else:
            return highest_player_result.player_id


def _get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size
