from django.db import models
from django.db.models.signals import post_save
from django.core.cache import cache
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
        
def match_post_save(sender, **kwargs):
    cache.delete('players')
post_save.connect(match_post_save, sender=Match)
    
class PlayerResult(models.Model):
    match = models.ForeignKey(Match)
    player = models.ForeignKey(Player)
    sum_spades = models.PositiveSmallIntegerField()
    sum_queens = models.PositiveSmallIntegerField()
    sum_solitare_lines = models.PositiveSmallIntegerField()
    sum_solitare_cards = models.PositiveSmallIntegerField()
    sum_pass = models.PositiveSmallIntegerField()
    sum_grand = models.PositiveSmallIntegerField()
    sum_trumph = models.PositiveSmallIntegerField()
    def total(self):
        return self.sum_spades+self.sum_queens+self.sum_solitare_lines+self.sum_solitare_cards+self.sum_pass-self.sum_grand-self.sum_trumph
    def __unicode__(self):
        return ""