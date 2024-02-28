from datetime import datetime
from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from core.context_processor import site_data
from django.utils.html import strip_tags
from django.http import Http404, HttpResponse, HttpResponseRedirect
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
    get_activity_kw_data, 
    get_blogs, 
    # get_services,
    get_category_with_count,
    get_top_views,
    get_blog_archive,
    get_4_parameter
    )
from .models import *
from .forms import *
import calendar
from django.views.decorators.cache import cache_control

from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType

import logging
log =  logging.getLogger('log')


def get_context_data(request, site, username=None):
    categories, top_views, blog_archive, featured_blogs = get_4_parameter()
    
    filters = {}  
     
    context = {     
        'site_data': site,
        'top_views': top_views,   
        'featured_blogs': featured_blogs,
        'filters': filters, 
    }   
    
    
    if 'q' in request.GET or 'selected_category' in request.GET or 'selected_archive' in request.GET:
        search_form = NewsSearchForm(request.GET)
        if search_form.is_valid():       
            q = search_form.cleaned_data.get('q', '')
            selected_category = search_form.cleaned_data.get('selected_category', [])
            selected_archive = search_form.cleaned_data.get('selected_archive', [])
            
            q_query = Q()
            if q:
                filters.update({'q' : [q]})
                q_query = Q(title__icontains=q) | Q(body__icontains=q)
             
            category_query = Q()   
            if len(selected_category) > 0:               
                filters.update({'selected_category' : [sc_slug for sc_slug in selected_category]})
                category_query = Q(categories__slug__in=selected_category)          
              
            archive_queries = Q()     
            if len(selected_archive) > 0:                         
                for archive in selected_archive:                    
                    filters.update({'selected_archive' : [sa for sa in selected_archive]})                    
                    archive_date = datetime.strptime(archive, "%B-%Y")
                    archive_queries |= Q(updated_at__year=archive_date.year) & Q(updated_at__month=archive_date.month)
            
            query = (q_query | category_query) & archive_queries
            
            if username is not None:
                blogs = Blog.published.filter(query, creator__username = username).order_by('-updated_at').distinct()
            else:
                blogs = Blog.published.filter(query).order_by('-updated_at').distinct()
                
        else:
            if username is not None:
                blogs = Blog.published.filter(creator__username = username).order_by('-updated_at')
            else:
                blogs = Blog.published.all().order_by('-updated_at')
                
            context.update({'blogs' : blogs})
            context.update({'search_form' : search_form})
            
            return context
    else:
        search_form = NewsSearchForm()
        if username is not None:
            blogs = Blog.published.filter(creator__username = username).order_by('-updated_at')
        else:
            blogs = Blog.published.all().order_by('-updated_at')
        
        
    paginator = Paginator(blogs, 10)
    page_number = request.GET.get('page')

    try:
        latest = paginator.page(page_number)
    except PageNotAnInteger:
        latest = paginator.page(1)
    except EmptyPage:
        latest = paginator.page(paginator.num_pages)
        
    context.update({'blogs' : latest})
    context.update({'search_form' : search_form})
    
    return context
    

def user_blogs(request, username):
    
    template_name = 'cms/category_details.html'   
   

    site = site_data()     
    
    site['title'] = f'Latest Blogs of Creator: {username}'    
    site['description'] = f"Welcome to {username}'s blog, where you'll find a wealth of valuable insights and personal experiences. Explore a diverse range of topics, including {username}'s areas of expertise or interests, and gain unique perspectives on relevant industry or subject. Expand your knowledge and engage with thought-provoking content on {username}'s blog."
    
    context = get_context_data(request, site, username=username)
    
    
    return render(request, template_name, context=context)
    

def latest_blogs(request):
    template_name = 'cms/category_details.html'      

    site = site_data()   
    
    site['title'] = f'Latest Published Blogs'
    site['description'] = 'Stay informed with the latest insights and updates from SINCEHENCE LTD. Explore our blog to discover valuable information, industry trends, and expert advice on wholesale trade, IT consultancy, data processing, and more. Stay connected and enhance your knowledge with our informative blog posts.'

    context = get_context_data(request, site, username=None)
    
    return render(request, template_name, context=context)


def page_detail(request, slug):
    template_name = 'cms/page_detail.html'
    
    page = get_object_or_404(Page, slug=slug) 
    
    page.view(request)     
    
    site = site_data()
    site['title'] = page.title
    site['description'] = page.meta_description
 
    
    
    
    
    context = {
        'page' : page,
        'site_data' : site
    }
    
    return render(request, template_name, context=context)   


 
def blog_detail(request, slug):
    template_name = 'cms/blog_detail.html'
    
    blog = get_object_or_404(Blog.published.prefetch_related('categories', 'blog_comments'), slug=slug)   
     
    blog.view(request)    
    
    comments = blog.blog_comments.filter(parent=None).order_by('-created_at')
    comment_form = BlogCommentForm()
    
    site = site_data()
    site['title'] = blog.title[:45]
    truncated_string = strip_tags(blog.body)[:160]
    site['description'] = truncated_string
    site['og_image'] = blog.feature.url
    
    context = {      
        'blog' : blog,   
        'site_data' : site,    
        'comments' : comments  
    }
    
    

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponse('Need to login', status=403)
            
        comment_form = BlogCommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.blog = blog
            new_comment.user = request.user            
            new_comment.save()    
            request.user.record_activity(get_activity_kw_data('Posted comment', new_comment))  
            return render(request, 'cms/comments.html', context={'comments' : comments})
        else:
            context.update({'comment_form' : comment_form})
            return render(request, template_name, context=context)    
    
    context.update({'comment_form' : comment_form})       
    
    return render(request, template_name, context=context)

def proccess_reply(request, blog_id, parent_id):
    if not request.user.is_authenticated:
        return HttpResponse('Need to login', status=403)
        
    try:
        blog = Blog.objects.get(id = blog_id)  
    except:
        return HttpResponse('Blog not found', status=404)
    
    try:
        parent = get_object_or_404(BlogComments, id=parent_id) 
    except:
        return HttpResponse('Should have parent!', status=404)    
    
    replies = BlogComments.objects.filter(blog = blog, parent = parent).order_by('-created_at') 
    
    reply_form = BlogCommentForm()
    
    if request.method == 'POST':
        reply_form = BlogCommentForm(request.POST)
        if reply_form.is_valid():
            new_comment = reply_form.save(commit=False)
            new_comment.blog = blog
            new_comment.user = request.user            
            new_comment.parent = parent
            new_comment.save()
            request.user.record_activity(get_activity_kw_data('Posted Reply', new_comment))     
            replies = BlogComments.objects.filter(blog = blog, parent = parent).order_by('-created_at') 
            return render(request, 'cms/replies.html', {'replies' : replies, 'c':parent})
        else:
            return render(request, 'cms/reply_form.html', {'replies' : replies,'reply_form' : reply_form, 'c':parent})
        
    return render(request, 'cms/reply_form.html', {'replies' : replies,'reply_form' : reply_form, 'c':parent})

def delete_reply(request, parent_id, reply_id):
    try:
        reply = BlogComments.objects.get(id = reply_id)
    except:
        return HttpResponse('Not a valid reply intented to delete!', status=404)
        
    if request.user.id != reply.user.id:
        return HttpResponse('You can not delete this reply!', status=403)
    else:    
        reply.delete()
        request.user.record_activity(get_activity_kw_data('Deleted Reply', reply))     
    parent = BlogComments.objects.get(id = parent_id)
    replies = BlogComments.objects.filter(parent = parent).order_by('-created_at')
        
    
    return render(request, 'cms/replies.html', {'replies' : replies, 'c': parent })

def delete_comments(request, blog_id, comment_id):
    try:
        comment = BlogComments.objects.get(id=comment_id)
    except:
        return HttpResponse('Not a valid comments intented to delete!', status=404)
    
    if request.user.id != comment.user.id:
        return HttpResponse('You can not delete this comment!', status=403)
    else:    
        comment.delete()
        request.user.record_activity(get_activity_kw_data('Deleted', comment))     
    
    blog = Blog.objects.get(id=blog_id)

    comments = BlogComments.objects.filter(blog__id = blog_id, parent=None).order_by('-created_at')
    
    return render(request, 'cms/comments.html', {'comments' : comments, 'blog' : blog})





from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

def handle_action(request, content_type_id, obj_id, action):
    try:
        content_type = ContentType.objects.get(id=content_type_id)
        # Get the model class
        model_class = content_type.model_class()
        # Get the model object
        obj = model_class.objects.get(id=obj_id)

        # Check if the user has permission to perform the action
        if not request.user.is_authenticated:
            raise PermissionDenied("You don't have permission to perform this action.")

        # Get or perform the action based on the provided action parameter
        if action == Action.LIKE:
            obj.like(request)           
            request.user.record_activity(get_activity_kw_data('Liked', obj))
        elif action == Action.DISLIKE:
            obj.dislike(request)  
            request.user.record_activity(get_activity_kw_data('Revoked Like', obj))                   
        else:
            log.error(f'invalid action in handle_action')
            return HttpResponse('error400')
        log.error(f'action handle success')
        return render(request, 'cms/like_dislike.html', {'obj': obj})

    except ObjectDoesNotExist:
        return HttpResponse('error404')

    except PermissionDenied as e:
        log.error(f'{e}')
        return HttpResponse('error403')

    except Exception as e:
        log.error(f'{e}')
        return HttpResponse('error400')
    
            
