import calendar
from django import template

register = template.Library()

def month_name(month_number):
    return calendar.month_name[month_number]
register.filter('month_name', month_name)