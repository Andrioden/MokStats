from django.http import HttpResponse
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from models import Match, PlayerResult

def last_playerlist(request):
    last_match_id = Match.objects.order_by('-id').values('id')[0]['id']
    player_ids = PlayerResult.objects.filter(match=last_match_id).order_by('id').values_list('player__id', flat=True)
    return HttpResponse(simplejson.dumps(list(player_ids), cls=DjangoJSONEncoder))