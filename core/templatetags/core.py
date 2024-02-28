import json
from django import template

from cms.models import Action
from core.agent_helper import get_client_ip
from core.helper import converted_amount
from django.template.loader import render_to_string
from service.models import ProjectTodo



from sourcing.views import get_paginated_items


register = template.Library()

@register.filter
def price_with_sign_symbol(value, trans):
    sign = '+' if trans.trans_type == 'add' else '-'
    if trans.trans_type == 'add':
        sign = '+'
        bsclass = 'text-success'
    elif trans.trans_type == 'sub':
        sign = '-'
        bsclass = 'text-danger'
    formation = f'{sign}{trans.paymemt_currency.symbol}{value}'
    return f'<span class="{bsclass}">{formation}</span>'

@register.filter
def get_start_end(order):
    if order.price.is_onetime:
        start_date = order.start_date.strftime('%Y-%m-%d') if order.start_date else None  # Format the start date as desired
        tentative_delivery = order.tentative_delivery.strftime('%Y-%m-%d') if order.tentative_delivery else None  # Format the delivery date as desired
        return f'Placed: {start_date}</br>Tentative Delivery: {tentative_delivery}</br>'
    if order.price.is_subscription:
        start_date = order.start_date.strftime('%Y-%m-%d') if order.start_date else None   # Format the start date as desired
        end_date = order.end_date.strftime('%Y-%m-%d') if order.end_date else None # Format the end date as desired
        return f'Subscription start at: {start_date}</br> Subscription End: {end_date}</br>'

@register.filter
def divide(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, ZeroDivisionError):
        return None
    
@register.filter(name='divisibleby')
def divisibleby(value, arg):
    return value % arg == 0

@register.filter(name='get_replies')
def get_replies(comment):
    return comment.child.all()

@register.filter(name='get_meta_service_type')
def get_meta_service_type(service):
    meta_data = service.service_meta_data.filter(key='service_type')
    if meta_data.exists():
        return meta_data.first().data        
    return ''

@register.filter(name="get_price_option_form")
def get_price_option_form(service, request):
    from service.views import get_formatted_prices
    from service.forms import ServicePriceForm
    
    formatted_prices = get_formatted_prices(service, request.currency)
    form = ServicePriceForm(prices=service.prices_of_service.all(), formatted_prices=formatted_prices)
    return form
    
@register.simple_tag
def calculate_col_ratios(loop_counter, ratio_string):
    ratio_list = [int(x) for x in ratio_string.split(":")]    
    # Calculate the effective index within the ratio_list
    effective_index = (loop_counter - 1) % len(ratio_list)
    return ratio_list[effective_index]

@register.filter
def range_filter(value):
    return range(value)

def price_msg(price_obj):
    if price_obj.is_onetime:
        data = f'Will be completed by { price_obj.interval_count } { price_obj.interval }<br />'   
        return data
    if price_obj.is_subscription:     
        data = f'Per { price_obj.interval_count } { price_obj.interval } Price'
        return data
    return None

def title_and_price(price_obj, code):
    symbol, amount = converted_amount(price_obj, code)    
    data = f'<b>{price_obj.name.upper()} - {symbol}{amount}</b><br />'
    return data
    
@register.filter
def formatedprice(price_obj, code, Story=None):
    
    data = title_and_price(price_obj, code)
    
    if Story is not None:
        data += '------------------------------------------------<br />'
    else:
        data += '<hr>'
        
    data += price_msg(price_obj)
    
    if Story is not None: 
        data += '------------------------------------------------<br />'
    else:
        data += '<hr>'
    data += f'{price_obj.features}'    


    return data


@register.filter
def convert_amount(price_obj, code):
    symbol, amount = converted_amount(price_obj, code)

    return str(symbol) + str(amount)

@register.filter
def remove_dash_hyphen_capital(value):
    data = value.replace('-', ' ').replace('_', ' ').capitalize()
    return data

@register.filter
def json_to_listify(value, arg):
    to_pylist = json.loads(value)
    return to_pylist[int(arg)]

@register.filter
def get_user_identity(user_obj):
    name = user_obj.get_full_name() or user_obj.username
    data = f"{name.upper()}<br />"
    data += f"{user_obj.email}<br />"
    data += f"{user_obj.phone if user_obj.phone else 'Phone number not found'}<br />"
    data += f"{user_obj.organization if user_obj.organization else 'Orgonization not found'}<br />"
    data += f"{user_obj.profile.location if user_obj.profile.location else 'Location not found'}<br />"    
    
    
    return data
    
@register.filter(name='uuid_str')
def uuid_str(value):
    return str(value)


@register.filter(name='get_path_list')
def get_path_list(request):
    from urllib.parse import urlparse, parse_qs
    url = request.get_full_path()
    parsed_url = urlparse(url) 
    query_params = parse_qs(parsed_url.query)    
    data_list = [query.replace('_page', '') for query in query_params]

    return data_list

@register.filter(name='get_paginated')
def get_paginated(items, request):   
    results = get_paginated_items(request, items.model)
    return results

@register.filter
def get_model_name(queryset):
   
    model_name = queryset.object_list[0]._meta.model_name
    
    return model_name

@register.filter
def is_liked_by_user(obj, request):   
    actions = Action.objects.filter(content_type=obj.get_content_type, action_type=Action.LIKE, object_id = obj.id)
    if request.user.is_authenticated:
        actions = actions.filter(user=request.user)
        return actions.exists()
    return False

@register.filter
def get_striped(value):
    
    return str(value).replace(' ', '').replace('|', '').strip()


@register.filter(name='get_project_issues')
def get_project_issues(value):
    ordertex_obj = value
    project_todo = ProjectTodo.objects.filter(reference = ordertex_obj).order_by('sort_order')
    return project_todo


def replacements(request):
    from django.urls import reverse
    if request.user.is_authenticated:
        if request.user.has_approved:    
            expert_profile_url = reverse('accounts:expert_profiles')
            expert_profile_url_value = f'<a class="btn btn-danger btn-lg" href="{expert_profile_url}">Create Expert Profile</a>'
        else:
            expert_profile_url = '#'
            expert_profile_url_value = f'<a class="btn btn-light btn-lg" href="{expert_profile_url}">You are not verified</a>'
    else:
        expert_profile_url = '#'
        expert_profile_url_value = f'<a class="btn btn-light btn-lg" href="{expert_profile_url}">You are not verified</a>'
        
    
        
    verification_request_url = reverse('accounts:verification_request')
    
    replacements = {
        '`expert_profile_url`':expert_profile_url_value,
        '`verification_request_url`': f'<a class="btn btn-danger btn-lg" href="{verification_request_url}">Submit Verification Request</a>',
    }
    return replacements


@register.filter(name='check_parameter')
def check_parameter(value, request):
    for key, replacement in replacements(request).items():
        value = value.replace(key, replacement)
    return value




