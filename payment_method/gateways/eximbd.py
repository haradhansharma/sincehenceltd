import os
import sys

from django.urls import reverse
from .base import PaymentGatewayBase

class EximBdPaymentGateway(PaymentGatewayBase):
    def __init__(self):        
        pass
    
    def allowed_amount(self):
        min = 0
        max = 199000
        any = True
        return min, max, any
    
    def allowed_countries(self):
        countries = ['BD']
        any = True
        return countries, any
    
    def get_help_text(self):
        return f'Exin Bank BD'
    
    def get_pay_to(self):
        return 'Haradhan Sharma'
    
    def get_account(self):
        
        rs = f'0112009414723<br/>'
        rs += f'Islampur Branch, Dhaka'
        
        return rs
    
    
    def get_gateway_instruction(self, order):
        message = f'Selected payment gateway is Exim Bank Bangladesh Limited. In the next screen there will be an invoice and instructions to pay.'
        return message
    
    @property
    def get_required_dict(self):
        dict = {
            'order_id': ''
        }
        return dict       

    def create_payment(self, **kwargs):        
        if not super().kwargs_is_valid(**kwargs):
            raise ValueError('Passed kwargs are not the same or have missing values!') 
        
        order_id = kwargs['order_id']        
        
        return reverse('payment_method:exim_bd', args=[int(order_id)])
    
    def process_payment(self, payment_data):
        pass
    
    def get_supported_currencies(self):
        pass
    
    def get_payment_details(self, payment_id):
        pass
    
    