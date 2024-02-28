from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from core.context_processor import site_data
from django.utils.html import strip_tags
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from core.agent_helper import get_client_ip
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random
from django.views.generic.edit import CreateView
from django.db.models import Count, Q
from core.helper import (
    custom_send_mail, 
    custom_send_mass_mail, 
    get_blogs,
    get_featured, 
    # get_services,
    get_service_categories,
    get_category_with_count,
    get_top_views,
    get_blog_archive
    )
from .models import *
from cms.models import *

from .forms import *
import calendar
from django.views.decorators.cache import cache_control

import logging
log =  logging.getLogger('log')


# Create your views here.

def home(request):
    template_name = 'core/home.html'    
        
    site = site_data()
    site['title'] = site.get('slogan')    
   
    latest_news = get_featured()

    about_us_link = get_object_or_404(Page, slug='about-us').get_absolute_url()
    
    service_categories = get_service_categories()  
    
    context = {    
        'site_data' : site,
        'latest_news' : latest_news,
        'about_us_link': about_us_link,
        'service_categories' : service_categories
        # 'services' : services
    }
    return render(request, template_name, context=context)





    



    