
from django.urls import path, include
from .views import *


app_name = 'payment_method'

urlpatterns = [
    # path('stripe-webhook/', stripe_webhook,  name='stripe_webhook'),
    path('bkash-manual/<uuid:order_id>', bkash_manual,  name='bkash_manual'),
    path('rocket-manual/<uuid:order_id>', rocket_manual,  name='rocket_manual'),
    path('exim-bd/<uuid:order_id>', exim_bd,  name='exim_bd'),
    
    
    
    
]
