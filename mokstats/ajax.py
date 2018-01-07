from django.http import HttpResponse
import json
from django.core.serializers.json import DjangoJSONEncoder
from models import Match, PlayerResult
from django.core.cache import cache
from django.views.decorators.cache import never_cache


@never_cache
def last_playerlist(request):
    last_match_id = Match.objects.order_by('-id').values('id')[0]['id']
    player_ids = PlayerResult.objects.filter(match=last_match_id).order_by('id').values_list('player__id', flat=True)
    return _json_response(list(player_ids))


@never_cache
def clear_cache(request):
    cache.clear()
    return _json_response({'response': "OK"})


def _json_response(data):
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder))