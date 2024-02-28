
from django.urls import path
from .views import *


app_name = 'cms'

urlpatterns = [   
    path('b/<str:slug>/', blog_detail, name='blog_details'),
    path('latest/blogs/', latest_blogs, name='latest_blogs'),       
    path('<str:username>/blogs/', user_blogs, name='user_blogs'), 
    # path('category/<str:slug>', category_detail, name='category_detail'),    
    # path('archive/<int:year>/<int:month>', archive_detail, name='archive_detail'),   
    path('p/<str:slug>', page_detail, name='page_detail'),   
    path('c/<int:blog_id>/<int:parent_id>', proccess_reply, name='proccess_reply'),   
    path('c/delete_reply/<int:parent_id>/<int:reply_id>', delete_reply, name='delete_reply'),  
    path('c/delete_comments/<int:blog_id>/<int:comment_id>', delete_comments, name='delete_comments'),   
     path('action/<int:content_type_id>/<int:obj_id>/<str:action>/', handle_action, name='handle_action'),
     

]