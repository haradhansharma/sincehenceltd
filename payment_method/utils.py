import os
# from django.conf import settings
from importlib import import_module
from django.conf import settings
from payment_method.gateways.base import PaymentGatewayBase

def get_payment_method_class(file_name):
    # Define the directory where payment method classes are located
    gateway_dir = os.path.join(settings.BASE_DIR, 'payment_method', 'gateways')

    # Iterate through files in the 'gateways' directory
    for file in os.listdir(gateway_dir):
    
        if file.endswith('.py') and file_name in file:
            module_name = file[:-3]
            module_path = f'payment_method.gateways.{module_name}'

            # Load the module dynamically
            module = import_module(module_path)

            # Get the class dynamically
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if hasattr(attr, '__bases__') and PaymentGatewayBase in attr.__bases__:
                    return attr

    return None