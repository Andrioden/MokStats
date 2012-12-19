# -*- coding: utf-8 -*-

from mokstats.models import *
from django.contrib import admin
from django import forms
import math

admin.site.register(Player)
admin.site.register(Place)

class ResultInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        # get forms that actually have valid data
        player_count = 0
        spades_total = 0
        queens_total = 0
        pass_total = 0
        grand_total = 0
        trumph_total = 0
        for form in self.forms:
            try:
                if form.cleaned_data:
                    sum_queens = form.cleaned_data['sum_queens']
                    if not sum_queens%4 == 0:
                        raise forms.ValidationError('Ulovlig dameverdi, %s er gitt, bare 4 er lovlig' % sum_queens)
                    player_count += 1
                    spades_total += form.cleaned_data['sum_spades']
                    queens_total += sum_queens
                    pass_total += form.cleaned_data['sum_pass']
                    grand_total += form.cleaned_data['sum_grand']
                    trumph_total += form.cleaned_data['sum_trumph']
            except AttributeError:
                pass
        if player_count < 3:
            raise forms.ValidationError('Minst 3 spillere')
        if not spades_total == 13:
            raise forms.ValidationError('For få/mange Spa poeng gitt, %s totalt nå, 13 krevd' % spades_total)
        if not queens_total == 16:
            raise forms.ValidationError('For få/mange Damer poeng gitt, %s totalt nå, 16 krevd' % queens_total)
        cards_per_player = 52/player_count
        if not pass_total == cards_per_player:
            raise forms.ValidationError('For få/mange Pass poeng gitt, %s totalt nå, %s krevd' % (pass_total, cards_per_player))
        if not grand_total == cards_per_player:
            raise forms.ValidationError('For få/mange Grand poeng gitt, %s totalt nå, %s krevd' % (grand_total, cards_per_player))
        if not trumph_total == cards_per_player:
            raise forms.ValidationError('For få/mange Trumf poeng gitt, %s totalt nå, %s krevd' % (trumph_total, cards_per_player))


class ResultInline(admin.TabularInline):
    exclude = ('rating',)
    readonly_fields = ['total',]
    model = PlayerResult
    formset = ResultInlineFormset

class MatchAdmin(admin.ModelAdmin):
    inlines = [ResultInline,]
    class Media:
        js = ("http://code.jquery.com/jquery-1.7.1.min.js",
              "admin_custom.js",)
        css = {'all': ('admin_custom.css',)}
admin.site.register(Match, MatchAdmin)