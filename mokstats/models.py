from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from mokstats.settings import CACHE_DIR
from rating import START_RATING
import os
import shutil
import datetime

""" SOME QUERIES """

class Player(models.Model):
    name = models.CharField(max_length=20)
    def get_ratings(self):
        results = PlayerResult.objects.filter(player=self).select_related('match__date')
        ratings = []
        prev_rating = START_RATING
        for res in results.order_by('match__date', 'match__id'):
            dif = res.rating-prev_rating
            if dif > 0:
                dif = "+"+str(dif)
                css_class = "positive"
            elif dif < 0:
                css_class = "negative"
            else:
                css_class = ""
            ratings.append([res.match.date.isoformat(), int(res.rating), 
                            css_class, str(dif), res.match_id])
            prev_rating = res.rating
        return ratings
    class Meta:
        ordering = ['name']
    def __unicode__(self):
        return self.name

class Place(models.Model):
    name = models.CharField(max_length=20)
    def __unicode__(self):
        return self.name
    
def get_last_match_date():
    match_count = Match.objects.count()
    if match_count == 0:
        return datetime.datetime.now()
    else:
        return Match.objects.all()[match_count-1].date
def get_last_match_place():
    match_count = Match.objects.count()
    if match_count == 0:
        return None
    else:
        return Match.objects.all()[match_count-1].place_id
class Match(models.Model):
    date = models.DateField(default=get_last_match_date)
    place = models.ForeignKey(Place, default=get_last_match_place)
    def get_winners(self):
        min_sum = 1000
        winners = []
        for result in PlayerResult.objects.filter(match=self):
            total = result.total()
            if total < min_sum:
                min_sum = total
                winners = []
                winners.append(result.player)
            elif total == min_sum:
                winners.append(result.player)
        return winners
    def get_positions(self):
        players = [{'id': res.player_id, 'total': res.total()} for res in PlayerResult.objects.filter(match=self)]
        splayers = sorted(players, key=lambda player: player['total'])
        for i in range(len(players)):
            players[i]['position'] = self.get_position(players[i]['id'], splayers)
        return players
    def get_position(self, pid, splayers=None):
        if not splayers:
            players = [{'id': res.player_id, 'total': res.total()} for res in PlayerResult.objects.filter(match=self)]
            splayers = sorted(players, key=lambda player: player['total'])
        for i in range(len(splayers)):
            if splayers[i]['id'] == pid:
                # Check if winner
                if splayers[i]['total'] == splayers[0]['total']:
                    return 1
                # Check if player got same total as someone ahead in the sorted list
                for pos in range(i): 
                    if splayers[i]['total'] == splayers[pos]['total']:
                        return pos+1
                # Check if player got same total as someone behind in the sorted list
                for pos in range(len(splayers)-1, i+1, -1):
                    if splayers[i]['total'] == splayers[pos]['total']:
                        return pos+1
                # Player did not have the same total as someone else
                return i+1
        print 'PlayerResult for player %s not found in match %s' % (pid, self.pk)
    def get_newer_matches(self):
        excludeQ = Q(date__lt=self.date) | (Q(date=self.date) & Q(id__lte=self.pk))
        return Match.objects.exclude(excludeQ)
    def get_older_matches(self):
        excludeQ = Q(date__gt=self.date) | (Q(date=self.date) & Q(id__gte=self.pk))
        return Match.objects.exclude(excludeQ)
    def get_next_match_id(self):
        newer = self.get_newer_matches()
        if newer.exists():
            return newer.order_by('date', 'id').values('id')[0]['id']
        else:
            return None
    def get_prev_match_id(self):
        older = self.get_older_matches()
        if older.exists():
            return older.order_by('-date', '-id').values('id')[0]['id']
        else:
            return None
    def __unicode__(self):
        return "%s - %s (ID: %s)" % (self.date, self.place.name, self.pk)
    class Meta:
        verbose_name = "Match"
        verbose_name_plural = "Matches" 
        
def delete_cache(sender, **kwargs):
    for root, dirs, files in os.walk(CACHE_DIR):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
post_save.connect(delete_cache, sender=Match)
post_delete.connect(delete_cache, sender=Match)

def clear_affected_results_rating(instance, **kwargs):
    newer = instance.get_newer_matches()
    newer_mids = list(newer.values_list('id', flat=True))
    affected_mids = newer_mids + [instance.id]
    PlayerResult.objects.filter(match_id__in=affected_mids).update(rating=None)
post_save.connect(clear_affected_results_rating, sender=Match)
post_delete.connect(clear_affected_results_rating, sender=Match)
    
class PlayerResult(models.Model):
    match = models.ForeignKey(Match)
    player = models.ForeignKey(Player)
    sum_spades = models.PositiveSmallIntegerField()
    sum_queens = models.PositiveSmallIntegerField()
    sum_solitaire_lines = models.PositiveSmallIntegerField()
    sum_solitaire_cards = models.PositiveSmallIntegerField()
    sum_pass = models.PositiveSmallIntegerField()
    sum_grand = models.PositiveSmallIntegerField()
    sum_trumph = models.PositiveSmallIntegerField()
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    def rating_dif(self):
        if not self.rating:
            return "?"
        older_matches = self.match.get_older_matches().values_list('id', flat=True)
        older_results = PlayerResult.objects.filter(player=self.player).filter(match__id__in=older_matches)
        if older_results.exists(): 
            return self.rating - older_results.order_by('-match__date', '-match__id')[0].rating
        else:
            return self.rating - START_RATING
    def vals(self):
        return {'player': {'id': self.player.id,
                           'name': self.player.name},
                'spades': self.sum_spades,
                'queens': self.sum_queens,
                'solitaire_lines': self.sum_solitaire_lines,
                'solitaire_cards': self.sum_solitaire_cards,
                'pass': self.sum_pass,
                'grand': self.sum_grand,
                'trumph': self.sum_trumph,
                'total': self.total(),
                'rating_change': self.rating_dif()}
    def total(self):
        return self.sum_spades+self.sum_queens+self.sum_solitaire_lines+self.sum_solitaire_cards+self.sum_pass-self.sum_grand-self.sum_trumph
    def __unicode__(self):
        return "Results for %s" % self.player.name
    class Meta:
        unique_together = ("match", "player")