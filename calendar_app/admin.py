from django.contrib import admin

from calendar_app.models import WeekendDay, OffDay

class WeekendDayAdmin(admin.ModelAdmin):
    pass

admin.site.register(WeekendDay, WeekendDayAdmin)


class OffDayAdmin(admin.ModelAdmin):
    list_display = ['selected_date', 'description']

admin.site.register(OffDay, OffDayAdmin)