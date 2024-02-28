from django.conf import settings  # Import Django project settings
import importlib  # Import the importlib module for dynamic imports

active_payment_methods = []  # Create an empty list to store active payment method instances

# Iterate through the list of active payment method paths defined in project settings
for path in settings.ACTIVE_PAYMENT_METHODS:
    # Split the path into the module path and the class name
    module_path, class_name = path.rsplit('.', 1)

    # Import the module dynamically using importlib
    module = importlib.import_module(module_path)

    # Get the payment gateway class from the imported module
    cls = getattr(module, class_name)

    # Create an instance of the payment gateway class and add it to the list
    active_payment_methods.append(cls())

