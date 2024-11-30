
from django.core.mail import get_connection
from django.apps import apps
# from .models import Page, Blog, Category, ResponseBackup
from django.core.cache import cache
from django.db.models import Count, Q
from django.utils import timezone
from django.db.models.functions import TruncMonth, TruncYear
from shcurrency.models import Currency
from django.conf import settings
from datetime import datetime, timedelta
from cms.models import (
    Category,
    Page,
    Blog,
    # OurService,
    Action
)
from service.models import (
    ServiceCategory
)
from django.contrib.sites.models import Site
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import cache_page

def build_full_url(path):
    """
    Build a full URL by appending a path to the domain of the current site.

    Args:
        path (str): The path or URL component to append.

    Returns:
        str: The full URL.
    """
    current_site = Site.objects.get_current()
    domain = current_site.domain

    # Check if the domain already contains 'http://' or 'https://'
    if not domain.startswith('http://') and not domain.startswith('https://'):
        protocol = 'https://' if current_site.domain.startswith('www.') else 'http://'
    else:
        protocol = ''

    # Ensure that the path starts with a forward slash
    if not path.startswith('/'):
        path = '/' + path

    # Construct the full URL
    full_url = f"{protocol}{domain}{path}"

    return full_url
def get_currencies():   
    
    currencies = cache.get('sh_currencies')
    if currencies is not None:
        return currencies

    currencies = Currency.objects.all()
    
    cache.set('sh_currencies', currencies, timeout=60 * 60) 
    return currencies


def get_blog_archive():

    blog_archives = cache.get('sh_blog_archives')
    if blog_archives is not None:
        return blog_archives

    blog_archives = Blog.published.annotate(
            month=TruncMonth('updated_at')                     
        ).values('month').annotate(total_blogs=Count('id')).order_by('-month')    
    
    cache.set('sh_blog_archives', blog_archives, timeout=60 * 60) 

    return blog_archives




def get_top_views():

    top_views_blog = cache.get('sh_top_views_blog')
    if top_views_blog is not None:
        return top_views_blog

    top_views_blog = Blog.published.annotate(
        total_view_count=Count('actions', filter=Q(actions__action_type=Action.VIEW))
    ).order_by('-total_view_count')[:3]  
    
    cache.set('sh_top_views_blog', top_views_blog, timeout=60 * 60) 
    return top_views_blog

def get_featured():

    featured_blog = cache.get('sh_featured_blog')
    if featured_blog is not None:
        return featured_blog

    featured_blogs = Blog.published.filter(is_featured = True).order_by('-updated_at')[:3]
    
    cache.set('sh_featured_blog', featured_blogs, timeout=60 * 60) 
    
    return featured_blog

def get_category_with_count():

    category_count = cache.get('sh_category_count')
    if category_count is not None:
        return category_count

    category_count = Category.objects.prefetch_related('blogs_category').annotate(blog_count=Count('blogs_category', filter=Q(blogs_category__status='published')))    
    
    cache.set('sh_category_count', category_count, timeout=60 * 60) 
    return category_count

def get_service_categories():
    categories = cache.get('sh_service_categories')
    if categories is not None:
        return categories
    categories = ServiceCategory.objects.filter(is_active = True).order_by('title')
    print(categories)
    cache.set('sh_service_categories', categories, timeout = 60 * 60) 
    
    return categories
# def get_services():

#     services = cache.get('sh_services')
#     if services is not None:
#         return services

#     services = OurService.objects.all()
#     cache.set('sh_services', services, timeout=60 * 60) 
#     return services


def get_blogs():

    blogs = cache.get('sh_blogs')
    if blogs is not None:
        return blogs


    blogs = Blog.published.all().order_by('-updated_at')
    cache.set('sh_blogs', blogs, timeout=60 * 60) 

    return blogs

def categories():
    categories = cache.get('sh_categories')
    if categories is not None:
        return categories
    categories = Category.objects.filter(is_active = True)
    cache.set('sh_categories', categories, timeout=60 * 60)  # Set a timeout of 60 minutes (in seconds)
    return categories


def pages():
    pages = cache.get('sh_pages')
    if pages is not None:
        return pages
    pages = Page.objects.filter(is_active = True) 
    cache.set('sh_pages', pages, timeout=60 * 60)  # Set a timeout of 60 minutes (in seconds)
    return pages

def get_consent_pages():
    pages = cache.get('sh_consent_pages')
    if pages is not None:
        return pages
    pages = Page.objects.filter(is_active = True, consent_required=True) 
    cache.set('sh_consent_pages', pages, timeout=60 * 60)  # Set a timeout of 60 minutes (in seconds)
    return pages






def model_with_field(field_name):    
    models_with_field_name = []
    # Iterate over all installed apps
    for app_config in apps.get_app_configs():
        # Get all models for the current app
        for model in app_config.get_models():
            # Check if the model has a field named 'field_name'
            if hasattr(model, field_name):
                models_with_field_name.append(model)
    return models_with_field_name

# Imported for backwards compatibility and for the sake
# of a cleaner namespace. These symbols used to be in
# django/core/mail.py before the introduction of email
# backends and the subsequent reorganization (See #10355)
from django.core.mail.message import (
    
    EmailMultiAlternatives,
    EmailMessage,

)

def custom_send_mail(
    subject,
    message,
    from_email,
    recipient_list,
    fail_silently=False,
    auth_user=None,
    auth_password=None,
    connection=None,
    html_message=None,
    cc=None,
    reply_to=None,
    bcc=None,
):
    """
    Easy wrapper for sending a single message to a recipient list. All members
    of the recipient list will see the other recipients in the 'To' field.

    If from_email is None, use the DEFAULT_FROM_EMAIL setting.
    If auth_user is None, use the EMAIL_HOST_USER setting.
    If auth_password is None, use the EMAIL_HOST_PASSWORD setting.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the EmailMessage class directly.
    """
    connection = connection or get_connection(
        username=auth_user,
        password=auth_password,
        fail_silently=fail_silently,
    )
    mail = EmailMultiAlternatives(
        subject, message, from_email, recipient_list, cc=cc, reply_to = reply_to, bcc=bcc, connection=connection
    )
    if html_message:
        mail.attach_alternative(html_message, "text/html")

    return mail.send()

def custom_send_mass_mail(
    datatuple, fail_silently=False, auth_user=None, auth_password=None, connection=None
):
    """
    Given a datatuple of (subject, message, from_email, recipient_list), send
    each message to each recipient list. Return the number of emails sent.

    If from_email is None, use the DEFAULT_FROM_EMAIL setting.
    If auth_user and auth_password are set, use them to log in.
    If auth_user is None, use the EMAIL_HOST_USER setting.
    If auth_password is None, use the EMAIL_HOST_PASSWORD setting.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the EmailMessage class directly.
    """
    connection = connection or get_connection(
        username=auth_user,
        password=auth_password,
        fail_silently=fail_silently,
    )
    messages = [
        EmailMessage(subject, message, sender, recipient, cc=cc, reply_to=reply_to, bcc=bcc, connection=connection)
        for subject, message, sender, recipient, cc, reply_to, bcc in datatuple
    ]
    return connection.send_messages(messages)


def converted_amount(price_obj, currency_code):
    currency = Currency.objects.filter(code = currency_code).first()
    current_rate = currency.rate    
    converted_amount = float(price_obj.amount) * float(current_rate)
    return currency, round(converted_amount, 2)




def calculate_delivery_date(start_date, interval):
    """
    Calculate the order delivery date based on the service interval.

    Args:
        start_date (datetime): The date when the service is sold.
        interval (str): The interval for service ('month', 'year', 'week', 'day').

    Returns:
        datetime: The calculated delivery date.
    """
    if interval == 'month':
        delivery_date = start_date + timedelta(days=30)  # Adding 30 days for a month interval.
    elif interval == 'year':
        delivery_date = start_date + timedelta(days=365)  # Adding 365 days for a year interval.
    elif interval == 'week':
        delivery_date = start_date + timedelta(weeks=1)  # Adding 1 week for a week interval.
    elif interval == 'day':
        delivery_date = start_date + timedelta(days=1)  # Adding 1 day for a day interval.
    else:
        raise ValueError("Invalid interval provided")

    return delivery_date


def get_4_parameter():
    categories = get_category_with_count()   
    
    top_views = get_top_views()    
    
    blog_archive =  get_blog_archive()
    
    featured_blogs =  get_featured()
    
    
    return categories, top_views, blog_archive, featured_blogs


def user_activities(request):
    user_activities = request.user.activities.all()
    latest_activities = user_activities[:10]
    all_activities = user_activities
    
    paginator = Paginator(all_activities, 10)
    page_number = request.GET.get('page')

    try:
        all_activities = paginator.page(page_number)
    except PageNotAnInteger:
        all_activities = paginator.page(1)
    except EmptyPage:
        all_activities = paginator.page(paginator.num_pages)
    
    return latest_activities, all_activities


def user_comments(request):
    user_comments = request.user.user_blog_comments.all()
    latest_comments = user_comments[:10]
    all_comments = user_comments
    
    paginator = Paginator(all_comments, 10)
    page_number = request.GET.get('page')

    try:
        all_comments = paginator.page(page_number)
    except PageNotAnInteger:
        all_comments = paginator.page(1)
    except EmptyPage:
        all_comments = paginator.page(paginator.num_pages)
    
    return latest_comments, all_comments

def get_activity_kw_data(msg, obj):
    # Check if 'msg' is provided
    if not msg:
        raise ValueError('Activity type is missing!')

    # Check if the object has 'get_absolute_url' defined
    if not hasattr(obj, 'get_absolute_url'):
        raise AttributeError('get_absolute_url method is not defined in the passed object!')

    # Gather data for activity
    data = {
        'ac_type': msg,
        'app_label': obj._meta.app_label,
        'app_model': obj._meta.model_name,
        'human_readable': obj._meta.verbose_name,
        'description': str(obj),
        'path': obj.get_absolute_url()
    }

    return data