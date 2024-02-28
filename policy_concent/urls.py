
from django.urls import path, include
from .views import *

app_name = 'policy_concent'

urlpatterns = [
    path('cookie-consent/', cookie_consent, name='cookie_consent'),
]