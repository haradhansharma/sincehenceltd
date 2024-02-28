import os
import sys


class PaymentGatewayBase:
    
    def get_pay_to(self):
        raise NotImplementedError("Subclasses must implement get_pay_to method")
    
    def get_account(self):
        raise NotImplementedError("Subclasses must implement get_account method")
    
    def allowed_amount(self):
        raise NotImplementedError("Subclasses must implement allowed_amount method")
    
    def allowed_countries(self):
        raise NotImplementedError("Subclasses must implement allowed_countries method")
    
    def get_help_text(self):
        raise NotImplementedError("Subclasses must implement get_help_text method")
    
    @property
    def get_required_dict(self):
        raise NotImplementedError("Subclasses must implement get_required_dict method")
    
    def kwargs_is_valid(self, **kwargs):
        # Check if all keys in kwargs are also present in get_required_dict
        if all(key in self.get_required_dict for key in kwargs):
            # Check if all values in kwargs are not None or empty strings
            if all(value is not None and value != '' for value in kwargs.values()):
                return True
            else:
                return False
        else:
            return False
    
    def create_payment(self, **kwargs):        
        raise NotImplementedError("Subclasses must implement create_payment method")
    
    def process_payment(self, payment_data):
        raise NotImplementedError("Subclasses must implement process_payment method")
    
    def refund_payment(self, payment_id, amount):
        pass
    
    def get_payment_status(self, payment_id):
        pass
    
    def get_supported_currencies(self):
        raise NotImplementedError("Subclasses must implement process_payment method")
    
    def get_payment_details(self, payment_id):
        '''
        method can be useful for retrieving detailed information about a specific payment, such as transaction history or metadata.
        '''
        raise NotImplementedError("Subclasses must implement process_payment method")
    
    
    def validate_payment_data(self, payment_data):
        '''
        method is a valuable addition to ensure that payment data is in the correct format before processing. This can help prevent errors and improve security.
        '''
        pass              
        

    def get_gateway_name(self):
        """Gets the Python file name that a class belongs to.

        Returns:
            The Python file name (without path and extension) that the class belongs to.
        """
        module = sys.modules[self.__module__]
        file_name = getattr(module, '__file__', None)
        if file_name is None:
            raise ValueError('The class {} does not have a file name.'.format(self))
        
        # Get the file name without path and extension
        return os.path.splitext(os.path.basename(file_name))[0]
        