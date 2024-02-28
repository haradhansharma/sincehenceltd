from django.urls import path, include
from .views import *
from .views import change_currency




app_name = 'shcurrency'



urlpatterns = [
    path('change-currency/', change_currency, name='change_currency'),
]
