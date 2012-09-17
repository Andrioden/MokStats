from mokstats.models import *
from django.contrib import admin

class PlayerAdmin(admin.ModelAdmin):
    pass
admin.site.register(Player, PlayerAdmin)

class ResultInline(admin.TabularInline):
    model = PlayerResult

class MatchAdmin(admin.ModelAdmin):
    inlines = [ResultInline,]

admin.site.register(Match, MatchAdmin)