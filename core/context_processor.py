import re
from django.conf import settings

from calendar_app.helpers import get_business_days, get_weekends
from .models import ExSite    
from django.core.cache import cache
from .models import *
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from .menus import (
    # category_menus,
    # page_menus,
    dashnoard_menu,
    footer_menu,
    header_menu,
    user_menu

)
from .helper import get_consent_pages, get_currencies

def site_data():
    data = cache.get('sh_site_data')
    if data is not None:
        return data
    try:
        site = ExSite.on_site.get()
    except:
        site = ExSite.objects.create(site=Site.objects.get(id=1))
    
    data = {
        'name' : site.site.name,
        'domain' : site.site.domain,
        'description': site.site_description,
        'author' : 'SINCEHENCE LTD',
        'meta_tag' : site.site_meta_tag,
        'favicon': site.site_favicon.url if site.site_favicon else '',
        'mask_icon': site.mask_icon.url if site.mask_icon else '',
        'logo': site.site_logo.url if site.site_logo else '',
        'trademark': site.trademark.url if site.trademark else '',       
        'slogan': site.slogan,
        'og_image': site.og_image.url if site.og_image else '',
        'facebook_link': site.facebook_link,
        'twitter_link': site.twitter_link, 
        'linkedin_link': site.linkedin_link,  
        'instagram_link': site.instagram_link,          
        'email': site.email,   
        'location': site.location,   
        'phone': site.phone,   
                 
    }

    cache.set('sh_site_data', data, timeout=3600)

    return data


def str_list_frm_path(request):   
    path = request.path

    # Split the path at each special character using a regular expression
    path_segments = re.split(r'[-_&/]', path)

    # Remove any empty strings from the list of path segments
    path_segments = [s for s in path_segments if s]
    return path_segments


def core_con(request):  
    import calendar

    context = {              
        # 'category_menus' : category_menus(request),
        # 'page_menus' : page_menus(request),
        'footer_menu' : footer_menu(request),
        'header_menu' : header_menu(request),
        'site_data' : site_data(),
        'currencies' : get_currencies(),
        'user_menu' : user_menu(request),
        'dashnoard_menu' : dashnoard_menu(request),
        'timezone' : settings.TIME_ZONE,
        'business_days' : get_business_days(),
        'office_start' : settings.OFFICE_START_TIME,
        'office_end' : settings.OFFICE_END_TIME,
        
        
 
     
    }
    
    return context