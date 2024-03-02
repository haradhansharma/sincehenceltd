from django.contrib import admin

from whoischeck.models import WhoisResult

class WhoisResultAdmin(admin.ModelAdmin):
    list_display = ('domain_name', 'registrar', 'registrant_name',)
    search_fields = ('domain_name', 'registrar', 'registrant_name',)
 
admin.site.register(WhoisResult, WhoisResultAdmin)
