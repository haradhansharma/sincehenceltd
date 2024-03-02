
from django.urls import path, include
from .views import *
from django.contrib.sitemaps.views import sitemap
from .sitemaps import *
from django.views.generic.base import TemplateView

app_name = 'core'

sitemap_list = {
    'static': StaticSitemap,
    'pages' : PageSitemap,
    'category' : CategorySitemap,
    'blogs' : BlogSitemap,
    'whois' : WhoisSitemap
}

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemap_list}, name='django.contrib.sitemaps.views.sitemap'),      
    path('', home, name='home'),
    
]
