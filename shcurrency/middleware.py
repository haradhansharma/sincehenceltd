from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .models import Currency

class CurrencyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # # Check if the user is authenticated and if the user has selected a currency
        # if 'currency' in request.session:
        #     currency_code = request.session['currency']
        #     try:
        #         # Get the Currency object based on the currency code stored in the session
        #         currency = Currency.objects.get(code=currency_code)
        #         # Set the currency in the request object
        #         request.currency = currency.code
        #     except Currency.DoesNotExist:
        #         # If the currency code is not found in the Currency model, set the default currency
        #         currency, created = Currency.objects.get_or_create(code=settings.DEFAULT_CURRENCY_CODE, name='US dollar', symbol='$', rate=1)
        #         request.currency = currency.code
        # else:
        #     # If the user is not authenticated or currency is not set in the session, set the default currency
        #     currency, created = Currency.objects.get_or_create(code=settings.DEFAULT_CURRENCY_CODE, name='Us dollar', symbol='$', rate=1)
        #     request.currency = currency.code
        
        # ================
        # # Check if the user is authenticated and if the user has selected a currency
        # if request.user.is_authenticated:
        #     # Option 1: Retrieve currency preference from user profile if available
        #     try:
        #         user_profile = UserProfile.objects.get(user=request.user)
        #         request.currency = user_profile.currency_preference
        #         return
        #     except UserProfile.DoesNotExist:
        #         pass  # Handle when user profile doesn't exist or doesn't have a currency set

            
        # Option 2: Fallback to session-based approach
        if 'currency' in request.session:
            currency_code = request.session['currency']
            try:
                currency = Currency.objects.get(code=currency_code)
                request.currency = currency.code
                return
            except Currency.DoesNotExist:
                pass  # Handle when the currency code is not found in the Currency model

        # Option 3: Fallback to default currency
        default_currency, created = Currency.objects.get_or_create(
            code=settings.DEFAULT_CURRENCY_CODE,
            name='US dollar',
            symbol='$',
            rate=1
        )
        request.currency = default_currency.code
            
   