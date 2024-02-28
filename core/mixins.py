from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.contrib import messages



from PIL import Image
from PIL.ExifTags import TAGS
from PIL import ExifTags
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile



class SaveFromAdminMixin:
    def save(self, request=None, *args, **kwargs):       
        
        
            
        if getattr(self, '_saving_from_admin', False):      
            super().save(request, *args, **kwargs)        
        else:   
            if not request:
                raise ValueError("The 'request' object is required to save the model.")

            if not request.user.is_authenticated:
                raise ValueError("The user must be logged in to save the model.")

            creator = self.get_creator_field_name()
            
            if not creator:
                raise ValueError("The 'get_creator_field_name' method must be implemented to save the model.")

            setattr(self, creator, request.user)
            
            sites = self.get_sites_field_name()
            
            if not sites:
                raise ValueError("The 'get_sites_field_name' method must be implemented to save the model.")                       
            
                
            title = self.get_title_field_name()
            
            if not title:
                raise ValueError("The 'get_title_field_name' method must be implemented to save the model.")
                    
            slug = self.get_slug_field_name()
            
            if not slug:
                raise ValueError("The 'get_slug_field_name' method must be implemented to save the model.")                   

            if not self.slug:
                # generate a slug based on the title
                self.slug = slugify(self.title)

            # check if the generated slug already exists
            original_slug = self.slug
            counter = 1
        
            while self.__class__.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
                if counter > 10:   
                    messages.error(request, 'Unable to generate a unique slug for the model!')           
                    raise ValidationError('Unable to generate a unique slug for the model!')  
                    
            super().save(request, *args, **kwargs)
            if not self.sites.exists():
                self.sites.add(request.site)                  


        if hasattr(self.__class__, 'append_to_save'):           
            self.append_to_save(request, *args, **kwargs)
            
   


    def get_creator_field_name(self):
        # This method should return the name of the field that refers to the user model, e.g. 'creator'
        raise NotImplementedError("The 'CreatorModelMixin' method must be implemented.")
    
    def get_sites_field_name(self):
        # This method should return the name of the field that refers to the sites model, e.g. 'creator'
        raise NotImplementedError("The 'SitesModelMixin' method must be implemented.")

    def get_title_field_name(self):
        # This method should return the name of the field that refers to the sites model, e.g. 'creator'
        raise NotImplementedError("The 'TitleAndSlugModelMixin' method must be implemented.")

    def get_slug_field_name(self):
        # This method should return the name of the field that refers to the sites model, e.g. 'creator'
        raise NotImplementedError("The 'TitleAndSlugModelMixin' method must be implemented.")




class CreatorModelMixin(models.Model):
    '''
    It will add `creator` ForeigKey field to the digignated model
    '''
    creator = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        editable=False,
        db_index=True,
        related_name='%(app_label)s_%(class)s_creator',
        # default=get_user_model().objects.get_or_create(username='haradhansharma', email='haradhan.sharma@gmail.com')[0].pk
    )
    def get_creator_field_name(self):
        return 'creator'

    class Meta:
        abstract = True
        
      

        
class TitleAndSlugModelMixin(models.Model):
    '''
    It will add `title` and `slug` field to te model
    '''
    title = models.CharField(_("Title"), max_length=250)
    slug = models.SlugField(verbose_name=_('Slug'), unique=True, db_index=True, max_length=250)
    
    def get_title_field_name(self):
        return 'title'
    
    def get_slug_field_name(self):
        return 'slug'
    
    
    class Meta:
        abstract = True
        
    
        
class SitesModelMixin(models.Model):
    
    '''
    It will add `sites` ManyToMany field to te model
    '''
    sites = models.ManyToManyField(Site, related_name='%(app_label)s_%(class)s_sites', db_index=True)
    
    
    def get_sites_field_name(self):
        return 'sites'
    
    class Meta:
        abstract = True
        
class IsActiveModelMixin(models.Model):
    '''
    It will add `is_active` BooleanField to te model with `default=True`
    '''
    is_active = models.BooleanField(default=True)

    
    class Meta:
        abstract = True
        
class MenuModelMixin(models.Model):
    
    '''
    It will add `add_to_page_menu`, `add_to_header_menu`, `add_to_footer_menu`,
    BooleanField to te model with `default=False`
    '''    
    add_to_page_menu = models.BooleanField(default=False)   
    add_to_header_menu = models.BooleanField(default=False)    
    add_to_footer_menu = models.BooleanField(default=False)   
    
    class Meta:
        abstract = True
        
class DateFieldModelMixin(models.Model):
    
    '''
    It will add `created_at`, `updated_at`,
    DateTimeField to te model.
    '''    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    
    class Meta:
        abstract = True
        
        
