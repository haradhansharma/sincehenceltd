from django.contrib import admin
from .models import *
from django_summernote.admin import SummernoteModelAdmin

# Register your models here.
class ExtendSiteOfSite(admin.StackedInline):
    model = ExSite
    can_delete = False   

class SiteAdmin(admin.ModelAdmin):
    list_display = ('domain', 'name')
    search_fields = ('domain', 'name')
    inlines = [ExtendSiteOfSite]    
admin.site.unregister(Site)
admin.site.register(Site, SiteAdmin)