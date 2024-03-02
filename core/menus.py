# from pprint import pprint
# from django.apps import apps
# from django.conf import settings
# from django.shortcuts import render
# from django.urls import reverse, reverse_lazy
# from django.utils.module_loading import import_string
# from django.contrib.auth.decorators import login_required
# from django.contrib.contenttypes.models import ContentType
# from django.templatetags.static import static
# # from core.models import (
# #     Category
# # )
from django.conf import settings
from django.urls import reverse
from core.helper import (
    pages,
    # categories,
    model_with_field,

)
from django.core.cache import cache
from django.templatetags.static import static


def dashnoard_menu(request):

    menu_items = []
      
    dashboard = {
        'title' : 'Dashboard',
        'url' : reverse('accounts:user_dashboard'),
        'data_set': False,
        'icon' : f'<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" viewBox="0 0 16 16" class="bi bi-house-door me-2">'
                    f'<path d="M8.354 1.146a.5.5 0 0 0-.708 0l-6 6A.5.5 0 0 0 1.5 7.5v7a.5.5 0 0 0 .5.5h4.5a.5.5 0 0 0 .5-.5v-4h2v4a.5.5 0 0 0 .5.5H14a.5.5 0 0 0 .5-.5v-7a.5.5 0 0 0-.146-.354L13 5.793V2.5a.5.5 0 0 0-.5-.5h-1a.5.5 0 0 0-.5.5v1.293L8.354 1.146ZM2.5 14V7.707l5.5-5.5 5.5 5.5V14H10v-4a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5v4H2.5Z"></path>'
                f'</svg>'
        
    }
    menu_items.append(dashboard)
    
    orders = {
        'title' : 'Orders',
        'url' : reverse('accounts:user_orders'),
        'data_set': False,
        'icon' : f'<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" viewBox="0 0 16 16" class="bi bi-cassette me-2">'
                    f'<path d="M4 8a1 1 0 1 0 0-2 1 1 0 0 0 0 2Zm9-1a1 1 0 1 1-2 0 1 1 0 0 1 2 0ZM7 6a1 1 0 0 0 0 2h2a1 1 0 1 0 0-2H7Z"></path>'
                    f'<path d="M1.5 2A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 14.5 2h-13ZM1 3.5a.5.5 0 0 1 .5-.5h13a.5.5 0 0 1 .5.5v9a.5.5 0 0 1-.5.5h-.691l-1.362-2.724A.5.5 0 0 0 12 10H4a.5.5 0 0 0-.447.276L2.19 13H1.5a.5.5 0 0 1-.5-.5v-9ZM11.691 11l1 2H3.309l1-2h7.382Z"></path>'
                f'</svg>'
        
    }
    menu_items.append(orders)
    
    due_orders = {
        'title' : 'Due',
        'url' : reverse('accounts:due_orders'),
        'data_set': False,
        'icon' : f'<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" viewBox="0 0 16 16" class="bi bi-cassette me-2">'
                    f'<path d="M4 8a1 1 0 1 0 0-2 1 1 0 0 0 0 2Zm9-1a1 1 0 1 1-2 0 1 1 0 0 1 2 0ZM7 6a1 1 0 0 0 0 2h2a1 1 0 1 0 0-2H7Z"></path>'
                    f'<path d="M1.5 2A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 14.5 2h-13ZM1 3.5a.5.5 0 0 1 .5-.5h13a.5.5 0 0 1 .5.5v9a.5.5 0 0 1-.5.5h-.691l-1.362-2.724A.5.5 0 0 0 12 10H4a.5.5 0 0 0-.447.276L2.19 13H1.5a.5.5 0 0 1-.5-.5v-9ZM11.691 11l1 2H3.309l1-2h7.382Z"></path>'
                f'</svg>'
        
    }
    menu_items.append(due_orders)
    
    incomplete_orders = {
        'title' : 'Incomplete',
        'url' : reverse('accounts:incomplete_orders'),
        'data_set': False,
        'icon' : f'<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" viewBox="0 0 16 16" class="bi bi-cassette me-2">'
                    f'<path d="M4 8a1 1 0 1 0 0-2 1 1 0 0 0 0 2Zm9-1a1 1 0 1 1-2 0 1 1 0 0 1 2 0ZM7 6a1 1 0 0 0 0 2h2a1 1 0 1 0 0-2H7Z"></path>'
                    f'<path d="M1.5 2A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 14.5 2h-13ZM1 3.5a.5.5 0 0 1 .5-.5h13a.5.5 0 0 1 .5.5v9a.5.5 0 0 1-.5.5h-.691l-1.362-2.724A.5.5 0 0 0 12 10H4a.5.5 0 0 0-.447.276L2.19 13H1.5a.5.5 0 0 1-.5-.5v-9ZM11.691 11l1 2H3.309l1-2h7.382Z"></path>'
                f'</svg>'
        
    }
    menu_items.append(incomplete_orders)
    
    
    
    projects = {
        'title' : 'Projects',
        'url' : reverse('accounts:user_projects'),
        'data_set': False,
        'icon' : f'<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" viewBox="0 0 16 16" class="bi bi-list-task me-2">'
                    f'<path fill-rule="evenodd" d="M2 2.5a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5V3a.5.5 0 0 0-.5-.5H2zM3 3H2v1h1V3z"></path>'
                    f'<path d="M5 3.5a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zM5.5 7a.5.5 0 0 0 0 1h9a.5.5 0 0 0 0-1h-9zm0 4a.5.5 0 0 0 0 1h9a.5.5 0 0 0 0-1h-9z"></path>'
                    f'<path fill-rule="evenodd" d="M1.5 7a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5H2a.5.5 0 0 1-.5-.5V7zM2 7h1v1H2V7zm0 3.5a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5H2zm1 .5H2v1h1v-1z"></path>'
                f'</svg>'
    }
    menu_items.append(projects)
    
    recents = {
        'title' : 'Activities',
        'url' : reverse('accounts:user_recents_activity'),
        'data_set': False,
        'icon' : f'<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" viewBox="0 0 16 16" class="bi bi-activity me-2">'
                    f'<path fill-rule="evenodd" d="M6 2a.5.5 0 0 1 .47.33L10 12.036l1.53-4.208A.5.5 0 0 1 12 7.5h3.5a.5.5 0 0 1 0 1h-3.15l-1.88 5.17a.5.5 0 0 1-.94 0L6 3.964 4.47 8.171A.5.5 0 0 1 4 8.5H.5a.5.5 0 0 1 0-1h3.15l1.88-5.17A.5.5 0 0 1 6 2Z"></path>'
                f'</svg>'
    }
    menu_items.append(recents)
    
    recents_comments = {
        'title' : 'Comments',
        'url' : reverse('accounts:user_recents_comments'),
        'data_set': False,
        'icon' : f'<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-chat-text-fill me-2" viewBox="0 0 16 16">'
                    f'<path d="M16 8c0 3.866-3.582 7-8 7a9.06 9.06 0 0 1-2.347-.306c-.584.296-1.925.864-4.181 1.234-.2.032-.352-.176-.273-.362.354-.836.674-1.95.77-2.966C.744 11.37 0 9.76 0 8c0-3.866 3.582-7 8-7s8 3.134 8 7zM4.5 5a.5.5 0 0 0 0 1h7a.5.5 0 0 0 0-1h-7zm0 2.5a.5.5 0 0 0 0 1h7a.5.5 0 0 0 0-1h-7zm0 2.5a.5.5 0 0 0 0 1h4a.5.5 0 0 0 0-1h-4z"/>'
                f'</svg>' 
    }
    menu_items.append(recents_comments)
        
    return menu_items




# def category_menus(request):
#     all_cat = categories().filter(add_to_cat_menu = True, sites__id = request.site.id) 
#     menu_items = []
#     for cat in all_cat:
#         if cat.have_items:         
#             item_dict = {
#                 'title' : cat.title,
#                 'url' : cat.get_absolute_url(),
#                 'data_set': False,
#                 'icon' : cat.icon
                
#             }
#             menu_items.append(item_dict)
        
#     return menu_items

def page_menus(request):
    
    menu_items = cache.get('sh_page_menu_items')
    if menu_items is not None:
        return menu_items
    
    all_page = pages().filter(add_to_page_menu = True, sites__id = request.site.id)     
    menu_items = []
    for p in all_page:
        item_dict = {
            'title' : p.title,
            'url' : p.get_absolute_url(), 
            'data_set': False  
        }
        menu_items.append(item_dict)    
    cache.set('sh_page_menu_items', menu_items, timeout=60 * 60)
        
    return menu_items




def footer_menu(request):
    
    menu_items = cache.get('sh_footer_menu_items')
    if menu_items is not None:
        return menu_items
    
    
    
    objects_with_footer_menu = []
    for model in model_with_field('add_to_footer_menu'):
        objects_with_footer_menu += model.objects.filter(add_to_footer_menu=True, sites__id = request.site.id).order_by('title')        
    menu_items = []     
    
    
    for obj in objects_with_footer_menu:
        item_dict = {
            'title' : obj.title,
            'url' : obj.get_absolute_url(),  
            'data_set': False 
        }
        menu_items.append(item_dict)      
        
        
    menu_items.append(
        {'title': 'Blog', 'url': reverse('cms:latest_blogs'), 'data_set': False},        
        ) 
    
    menu_items.append(
        {'title': 'Contact Us', 'url': reverse('contact:contact'), 'data_set': False},        
        ) 
    
    #Add more manual above this line ====================#        
    nav_one = []
    nav_two = []
    nav_three = []


    for mi in menu_items:        
        if len(nav_one) <= round(len(menu_items)/3)-1:
            nav_one.append(mi)
        elif len(nav_two) <= round(len(menu_items)/3)-1:            
            nav_two.append(mi) 
        else:
            nav_three.append(mi)             
      
    menu_pack = []    
    menu_pack.append(
        {'title': 'Navigation', 'url': '#navone', 'data_set': nav_one},        
        )         
    menu_pack.append(
        {'title': 'Continued', 'url': '#navtwo', 'data_set': nav_two},        
        )    
    menu_pack.append(
        {'title': 'Continued', 'url': '#navthree', 'data_set': nav_three},        
        )        
   
    
    cache.set('sh_footer_menu_items', menu_pack, timeout=60 * 60)
    
        
    return menu_pack

def header_menu(request):
    
    menu_items = cache.get('sh_header_menu_items')
    if menu_items is not None:
        return menu_items
    
    
    objects_with_header_menu = []

    for model in model_with_field('add_to_header_menu'):     
        objects_with_header_menu += model.objects.filter(add_to_header_menu=True, sites__id = request.site.id).order_by('title')
        
    menu_items = [] 
    menu_items.append(
        {'title': 'Home', 'url': '/', 'data_set': False},        
        )     
    
    menu_items.append(
        {'title': 'Page', 'url': False, 'data_set': page_menus(request) },        
        ) 
    for obj in objects_with_header_menu:
        have_items = getattr(obj, 'have_items', None)
        if (have_items and obj.have_items) or obj.add_to_header_menu:
            item_dict = {
                'title': obj.title,
                'url': obj.get_absolute_url(),
                'data_set': False
            }
            menu_items.append(item_dict)
            
    menu_items.append(
        {'title': 'Blogs', 'url': reverse('cms:latest_blogs'), 'data_set': False},        
        ) 
    
    if settings.SALING_SERVICE:
    
        product_menus =[]
        menu_items.append(
            {'title': 'Products', 'url': False, 'data_set': product_menus },        
            )   
        product_menus.append(
            {'title': 'Digital Products', 'url': reverse('service:service_list'), 'data_set': False},        
            )  
        
          
    tools_menus =[]
    menu_items.append(
        {'title': 'Tools', 'url': False, 'data_set': tools_menus },        
        )   
    tools_menus.append(
        {'title': 'Whois Check', 'url': reverse('whoischeck:check_whois'), 'data_set': False},        
        )  
    
    
    menu_items.append(
        {'title': 'Contact', 'url': reverse('contact:contact'), 'data_set': False},        
        ) 
    
    cache.set('sh_header_menu_items', menu_items, timeout=60 * 60)
        
    return menu_items


def user_menu(request):   
        
    menu_items = []     
    submenus = []   
    
    if request.user.is_authenticated:       
        item_dict_dash = {
            'title' : 'Dashboard',
            'url' : reverse('accounts:user_dashboard'), 
            'data_set': False  
        }
        submenus.append(item_dict_dash)     
        item_dict = {
            'title' : 'Profile Settings',
            'url' : reverse('accounts:profile_setting'), 
            'data_set': False  
        }
        submenus.append(item_dict)        
        item_dict2 = {
            'title' : 'Change Password',
            'url' : reverse('accounts:change_pass'), 
            'data_set': False  
        }
        submenus.append(item_dict2)        
        item_dict3 = {
            'title' : 'Logout',
            'url' : reverse('accounts:logout'), 
            'data_set': False  
        }
        submenus.append(item_dict3)   
        
              
        menu_items.append(
            {'title': request.user.username, 'url': request.user.avatar, 'data_set': submenus},        
            )    
    else:
        item_dict = {
            'title' : 'Login',
            'url' : reverse('accounts:login') + f'?next={request.path}', 
            'data_set': False  
        }
        submenus.append(item_dict)        
        item_dict2 = {
            'title' : 'SignUp',
            'url' : reverse('accounts:signup'), 
            'data_set': False  
        }
        submenus.append(item_dict2)        
        menu_items.append(
            {'title': 'Avatar', 'url': static('no_image.png') , 'data_set': submenus},        
            )   
 
    return menu_items



    



    