from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Currency
from urllib.parse import urlparse


def change_currency(request):
    if request.method == 'POST':
        currency_code = request.POST.get('currency')
        try:
            # Check if the selected currency exists in the Currency model
            currency = Currency.objects.get(code=currency_code)
            # Set the selected currency in the session
            request.session['currency'] = currency.code
            messages.success(request, 'Currency updated successfully.')
        except Currency.DoesNotExist:
            messages.error(request, 'Invalid currency selection.')

    referring_url = request.META.get('HTTP_REFERER')

    if referring_url:
        referring_parsed = urlparse(referring_url)
        current_parsed = urlparse(request.build_absolute_uri())
        
        if referring_parsed.hostname == current_parsed.hostname:
            return HttpResponseRedirect(referring_url)

    return HttpResponseRedirect('/')