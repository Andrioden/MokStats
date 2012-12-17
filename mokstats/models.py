from django.db import models
from django.db.models.signals import post_save, post_delete
from mokstats.settings import CACHE_DIR
from rating import START_RATING
import os
import shutil
import datetime

class Player(models.Model):
    name = models.CharField(max_length=20)
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

def remove_newer_result_ratings(instance, **kwargs):
    date = instance.date
    PlayerResult.objects.filter(match__date__gt=date).update(rating=None)
post_save.connect(remove_newer_result_ratings, sender=Match)
post_delete.connect(remove_newer_result_ratings, sender=Match)
    
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
        older_results = PlayerResult.objects.filter(player=self.player).filter(match__date__lt=self.match.date)
        if older_results.exists(): 
            return self.rating - older_results.order_by('-match__date', '-pk')[0].rating
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