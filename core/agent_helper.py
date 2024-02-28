#helper functions

from django.conf import settings
import requests

import logging
log =  logging.getLogger('log')


def get_client_ip(request):
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:        
        ip = x_forwarded_for.split(',')[-1].strip()    
    elif request.META.get('HTTP_CLIENT_IP'):        
        ip = request.META.get('HTTP_CLIENT_IP')
    elif request.META.get('HTTP_X_REAL_IP'):        
        ip = request.META.get('HTTP_X_REAL_IP')
    elif request.META.get('HTTP_X_FORWARDED'):        
        ip = request.META.get('HTTP_X_FORWARDED')
    elif request.META.get('HTTP_X_CLUSTER_CLIENT_IP'):        
        ip = request.META.get('HTTP_X_CLUSTER_CLIENT_IP')
    elif request.META.get('HTTP_FORWARDED_FOR'):        
        ip = request.META.get('HTTP_FORWARDED_FOR')
    elif request.META.get('HTTP_FORWARDED'):        
        ip = request.META.get('HTTP_FORWARDED')
    elif request.META.get('HTTP_VIA'):        
        ip = request.META.get('HTTP_VIA')    
    else:        
        ip = request.META.get('REMOTE_ADDR')
        
    return ip

#helper function
def get_agent(request):   
    
    results = {}        
    if request.user_agent.is_mobile:
        user_usage = 'Mobile'        
    elif request.user_agent.is_tablet:
        user_usage = 'Tablet'    
    elif request.user_agent.is_touch_capable:
        user_usage = 'Touch Capable'
    elif request.user_agent.is_pc :
        user_usage = 'PC'
    elif request.user_agent.is_bot :
        user_usage = 'BOT'
    else:
        user_usage = 'Not able to figur out'        
    
    data = {
        'user_usage' : user_usage ,
        'user_browser' : request.user_agent.browser,
        'user_os' : request.user_agent.os ,
        'user_device' : request.user_agent.device          
    }    
    results.update(data)
    
    
    return results


def get_location_info(request):
    """
    Get location information based on the user's IP address.

    This function uses the IP address of the user obtained from the `get_ip` function to retrieve
    location details from the IPinfo database. It uses the provided API token from the settings
    to authenticate the request. The function returns location-related data, including city, region,
    country, and more.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        dict: Location-related information obtained from the IPinfo database.
    """  
    log.info('Geting Location details based on IP')
    
    # Obtain user's IP address
    ip = get_client_ip(request)
    
    # Get IPinfo token from settings
    token = settings.IPINFO_TOKEN    
  
    # Construct the URL for IPinfo API request
    info_url = f'https://ipinfo.io/{ip}?token={token}'
    
    data = {}
    
    try:
        response = requests.get(info_url)
        if response.status_code == 200:
            data = response.json()
            data.update(data)  # Update the data dictionary with IP information
            log.info(f'Location data {data} found for user {request.user}')
        else:
            log.info(f'IPinfo API returned status code {response.status_code} for user {request.user}')
    except requests.RequestException as e:
        # Handle URL and HTTP errors
        log.error(f'Error while fetching location data for user {request.user}: {e}')
        
    return data



