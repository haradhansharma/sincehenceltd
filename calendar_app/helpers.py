from calendar_app.models import *
from django.core.cache import cache
from django.conf import settings

def get_weekends():
    cache_key = 'sh_weekend_days'
    weekends = cache.get(cache_key)
    
    if not weekends:
        weekends = list(WeekendDay.objects.values_list('day_of_week', flat=True))
        cache.set(cache_key, weekends)

    return weekends

def get_business_days():
    cache_key = 'sh_business_days'
    business_days = cache.get(cache_key)
    
    if not business_days:
        weekends = get_weekends()
        zero_based_array = [number for number, _ in settings.DAY_CHOICES]
        business_days = [day for day in zero_based_array if day not in weekends]
        cache.set(cache_key, business_days)

    return business_days

def get_offdays():
    cache_key = 'sh_off_days'
    offdays = cache.get(cache_key)
    
    if not offdays:
        offdays = OffDay.objects.all()
        cache.set(cache_key, offdays)

    return offdays
    