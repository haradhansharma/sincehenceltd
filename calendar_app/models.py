from django.db import models
import calendar

from sincehence import settings

class WeekendDay(models.Model):  

    day_of_week = models.PositiveSmallIntegerField(choices=settings.DAY_CHOICES)

    def __str__(self):
        return self.get_day_of_week_display()

class OffDay(models.Model):
    selected_date = models.DateField()
    description = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ('selected_date', )
