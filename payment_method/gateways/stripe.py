import os
from pprint import pprint
import sys
from django.conf import settings
import stripe
from .base import PaymentGatewayBase
from urllib.parse import urlparse, parse_qs

import logging
log =  logging.getLogger('log')


class StripePaymentGateway(PaymentGatewayBase):
    """
    StripePaymentGateway class for handling payments via Stripe.

    Inherits from PaymentGatewayBase to ensure a common interface for payment gateways.
    """

    def __init__(self):
        """
        Initialize the Stripe payment gateway with the Stripe secret key from Django settings.
        """
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        
    def get_help_text(self):
        return f'Safe & Secured. Supports a wide range of major payment methods!'

    def create_payment(self, **kwargs):
        """
        Create a payment using Stripe.

        This method should implement the logic for creating a payment with Stripe.

        Args:
            **kwargs: Additional keyword arguments for payment creation.

        Returns:
            None or PaymentResponse: The response from the payment gateway.
        """
        
        success_url = kwargs['success_url']
        
        # Check if 'session_id' and 'selected_gateway' are already in the URL
        parsed_url = urlparse(success_url)
        query_params = parse_qs(parsed_url.query)

        if 'session_id' in query_params and 'selected_gateway' in query_params:            
            pass
        else:
             raise ValueError("Required parameters 'session_id' and/or 'selected_gateway' are missing in the success_url construction!")
        
        line_items = [
                {
                    'quantity' : kwargs['line_items__quantity'],
                    'price_data' : {
                        'currency' : kwargs['line_items__price_data__currency'],
                        'unit_amount_decimal' : kwargs['line_items__price_data__unit_amount_decimal'], 
                        'tax_behavior' :  kwargs['line_items__price_data__tax_behavior'],  
                        'product_data' : {
                            'name' : kwargs['line_items__price_data__product_data__name'],
                            'description' : kwargs['line_items__price_data__product_data__description'],
                            'tax_code' : kwargs['line_items__price_data__product_data__tax_code'] 
                        }                
                    }
                }
            ]
        
        if kwargs['mode'] == 'subscription':            
            line_items[0]['price_data'].update(
                {
                    'recurring' : {
                        'interval' : kwargs['line_items__price_data__recurring__interval'],
                        'interval_count' : kwargs['line_items__price_data__recurring__interval_count']                        
                    } 
                    
                }
            )  
        
        after_expiration = {
                'recovery' : {
                    'enabled' : kwargs['after_expiration__recovery__enabled'],
                    'allow_promotion_codes' : kwargs['after_expiration__recovery__allow_promotion_codes'],                    
                } 
            }
        automatic_tax = {
                'enabled' : kwargs['automatic_tax__enabled']
            }
        phone_number_collection = {
                'enabled' : kwargs['phone_number_collection__enabled']
            }
        tax_id_collection = {
                'enabled' : kwargs['tax_id_collection__enabled']
            }
        
        para = {
            'success_url' : success_url,
            'cancel_url' : kwargs['cancel_url'],
            'client_reference_id' : kwargs['client_reference_id'],
            'currency' : kwargs['currency'],
            'mode' : kwargs['mode'],
            'locale' : kwargs['locale'],            
            'after_expiration' : after_expiration,
            'automatic_tax' : automatic_tax,
            'phone_number_collection' : phone_number_collection,
            'tax_id_collection' : tax_id_collection,   
                     
            'line_items' : line_items,
     
            
                    
        }
        
        
        customer_update = {
            'name' : 'auto'
        }
        
        
        
        if 'customer_email' in kwargs:
            para.update(
                {
                    'customer_email': kwargs['customer_email']
                }
            )     
            
        if 'customer' in kwargs:
            para.update({'customer': kwargs['customer']}) 
            para.update({'customer_update' : customer_update})     
       
        
        try:         
            session = stripe.checkout.Session.create(**para)        
            log.info(f'STRIPE CHECKEOUT SESSION CREATED SUCCESSFULLY!')
            return session.url
        except stripe.error.CardError as e:
            log.error(f'STRIPE CARD ERROR RECORDED: {e}')
        except stripe.error.InvalidRequestError as e:
            log.error(f'STRIPE INVALID REQUEST ERROR RECORDED: {e}')
        except stripe.error.APIConnectionError as e:
            log.error(f'STRIPE API CONNECTION ERROR RECORDED: {e}')
        except stripe.error.APIError as e:
            log.error(f'STRIPE API ERROR RECORDED: {e}')
        except stripe.error.AuthenticationError as e:
            log.error(f'STRIPE AUTHENTICATION ERROR RECORDED: {e}')
        except stripe.error.IdempotencyError as e:
            log.error(f'STRIPE IDEMPOTENCY ERROR RECORDED: {e}')
        except stripe.error.PermissionError as e:
            log.error(f'STRIPE PERMISSION ERROR RECORDED: {e}')
        except stripe.error.RateLimitError as e:
            log.error(f'STRIPE RATE LIMITE ERROR RECORDED: {e}')
        except stripe.error.SignatureVerificationError as e:
            log.error(f'STRIPE SIGNATURE VERIFICATION ERROR RECORDED: {e}')
        except Exception as e:
            log.error(f'AN ERROR IS RECORDED DURING CHECKOUT SESSION WHICH IS NOT RELATED TO THE STRIPE: {e}')        
            
        return None    
    
    def get_session_response(self, session_id):
        
        checkout_session = stripe.checkout.Session.retrieve(session_id, expand=['subscription'])       
        print(checkout_session)
        context = {
            'order_id' : checkout_session['client_reference_id'],
            'customer_email' : checkout_session['customer_details']['email'],
            'customer_phone' : checkout_session['customer_details']['phone'],
            'payment_intent' : checkout_session['payment_intent'],
            'payment_status' : checkout_session['payment_status'],
            'order_currency' : checkout_session['currency'],
            'amount_subtotal' : checkout_session['amount_subtotal'],
            'amount_total' : checkout_session['amount_total'],
            'automatic_tax_status' : checkout_session['automatic_tax']['status'] ,             
            'invoice_id' : checkout_session['invoice'] ,   
            'customer_id_gateway' : checkout_session['customer'], #if new   
            'mode' : checkout_session['mode'],
            'url' : checkout_session['url'],
            
        }
        if checkout_session['mode'] == 'subscription' and checkout_session['payment_status'] == 'paid':
            context.update(
                {
                    'created_date' : checkout_session['subscription']['current_period_start'],
                    'expires_at' : checkout_session['subscription']['current_period_end'],
                    'subscription_id' : checkout_session['subscription']['id'],
                }
            )
            
        
        return context
        

    def process_payment(self, payment_data):
        """
        Process a payment using Stripe.

        This method should implement the logic for processing a payment with Stripe.

        Args:
            payment_data (dict): Data related to the payment.

        Returns:
            None or PaymentResponse: The response from the payment gateway.
        """
        # Implement the payment processing logic here
        # Example: Use Stripe SDK to process the payment
        # return PaymentResponse or None

    def get_supported_currencies(self):
        """
        Get the list of supported currencies by Stripe.

        Returns:
            list: A list of supported currency codes.
        """
        # Implement logic to fetch supported currencies from Stripe
        # Example: Use Stripe SDK to get supported currencies
        # return list of currency codes

    def get_payment_details(self, payment_id):
        """
        Get details of a payment from Stripe.

        Args:
            payment_id (str): The unique identifier of the payment.

        Returns:
            dict or None: Details of the payment or None if not found.
        """
        # Implement logic to retrieve payment details from Stripe
        # Example: Use Stripe SDK to fetch payment details
        # return payment details as a dictionary    
    
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
