from django.db import models
from django.db.models.signals import post_save, post_delete
from mokstats.settings import CACHE_DIR
import os
import shutil
import datetime

class Player(models.Model):
    name = models.CharField(max_length=20)
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
                'total': self.total()}
    def total(self):
        return self.sum_spades+self.sum_queens+self.sum_solitaire_lines+self.sum_solitaire_cards+self.sum_pass-self.sum_grand-self.sum_trumph
    def __unicode__(self):
        return "Results for %s" % self.player.name