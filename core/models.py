from django.db import models
from django.contrib.sites.models import Site
from django.core.validators import FileExtensionValidator
from django.contrib.sites.managers import CurrentSiteManager

from django.utils.translation import activate, gettext_lazy as _

from django.core.validators import FileExtensionValidator
from django.contrib.sites.models import Site






# Create your models here.
class ExSite(models.Model):    
    site = models.OneToOneField(Site, primary_key=True, verbose_name='site', on_delete=models.CASCADE)   
    site_description = models.TextField(max_length=500, null=True, blank=True)
    site_meta_tag =models.CharField(max_length=255, null=True, blank=True)
    site_favicon = models.ImageField(upload_to='site_image/', null=True, blank=True)
    site_logo = models.ImageField(upload_to='site_image/', null=True, blank=True)
    trademark = models.ImageField(upload_to='site_image/', null=True, blank=True)
    slogan = models.CharField(max_length=150, default='', null=True, blank=True)
    og_image = models.ImageField(upload_to='site_image/', null=True, blank=True)
    mask_icon = models.FileField(upload_to='site_image/', validators=[FileExtensionValidator(['svg'])], null=True, blank=True)    
    facebook_link = models.URLField(null=True, blank=True)
    twitter_link = models.URLField(null=True, blank=True)
    linkedin_link = models.URLField(null=True, blank=True)    
    instagram_link = models.URLField(null=True, blank=True)  
    
    email = models.EmailField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=16, null=True, blank=True)
    
    
    objects = models.Manager()
    on_site = CurrentSiteManager('site')
    
    def __str__(self):
        return self.site.__str__()  