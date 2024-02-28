
from django.urls import path
from .views import *
from django.contrib.sitemaps.views import sitemap


app_name = 'contact'



urlpatterns = [
    path('', contact, name='contact'),   
  
    
]
