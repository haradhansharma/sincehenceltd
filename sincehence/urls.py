"""
URL configuration for sincehence project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import (
    webmanifest
    ) 



urlpatterns = [
    path('admin/', admin.site.urls),  
    path('summernote/', include('django_summernote.urls')),  
    path('', include('core.urls')),   
    path('services/', include('service.urls')),   
    path('accounts/', include('accounts.urls')),
    path('cms/', include('cms.urls')),
    path('contact/', include('contact.urls')),  
    path('payment-method/', include('payment_method.urls')), 
    path('consent/', include('policy_concent.urls')),  
    path('sourcing/', include('sourcing.urls')),
    path('shcurrency/', include('shcurrency.urls')),
    
]

urlpatterns += [    
    path('webmanifest/', webmanifest, name='webmanifest'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    

    

