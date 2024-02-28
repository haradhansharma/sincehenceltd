import re
from django.db import models
# from bds.models import BdService, PaymentMethod

import uuid
from django.db import models
from django.urls import reverse
from PIL import Image
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill, Resize, ProcessorPipeline
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from django.templatetags.static import static
from django_countries.fields import CountryField
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.validators import FileExtensionValidator


class ApprovalStatus(models.Model):
    title = models.CharField(
        max_length=150,
        unique=True,  # Enforce uniqueness
        validators=[
            RegexValidator(
                regex=r'^(approved|rejected|pending|modified)(?:-[\w-]*)?$',
                flags=re.IGNORECASE,  # Case-insensitive matching
                message="Title must be 'approved', 'rejected', or 'pending', optionally followed by a hyphen and additional words.",
            )
        ],
    )
    
    def __str__(self):        
        return f'{self.title}'
    

class QIUserManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError("The Email field must be set.")
        
        if not username:
            username = email.split('@')[0]
            username = GlobalUserModel.normalize_username(username)
            
        email = self.normalize_email(email)   
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, username=None, email=None, password=None, **extra_fields):
        return super(QIUserManager, self).create_user(username, email, password, **extra_fields)

    def create_superuser(self, username = None, email=None, password=None, **extra_fields):
        return super(QIUserManager, self).create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    
    username = models.CharField(
        _("username"),      
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
   
    email = models.EmailField('E-Mail Address', unique=True)
    phone = PhoneNumberField('Phone', blank=True, null=True)
    ######it can be save in separate database########
    # gateway_customer_reference = models.CharField(max_length=252, null=True, blank=True)
    organization = models.CharField(max_length=252, null=True, blank=True)   
     
    
    objects = QIUserManager()

    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def save(self, *args, **kwargs):
        if self.pk is None:  # If it's a new user being created
            # Logic for new user creation, which doesn't require changing the username as it is done in user manager
            pass
        else:  # If it's an existing user being updated
            try:
                original_object = User.objects.get(pk=self.pk)
            except User.DoesNotExist:
                original_object = None

            if original_object and self.username != original_object.username:  # Check if username is being updated
                base_username = self.username  # Regenerate base username
                username = base_username
                count = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}_{count}"
                    count += 1
                self.username = username

        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.email
    
    def get_absolute_url(self):        
        return reverse('accounts:user_link', args=[str(self.id)])
    
    @property
    def is_paid(self):
        return False
    
    @property
    def get_profile(self):
        return self.profile       
   
    
    @property
    def avatar(self):    
        if self.is_authenticated and hasattr(self, 'profile') and self.profile.avatar:  
            profile = self.profile   
            img = profile.avatar.url
        else:
            img = static('no_image.png')           

        return img
    
    
    def gateway_customer_reference(self, gateway):
        reference = self.gateway_references.filter(gateway = gateway)
        if reference.exists():
            return reference.first().reference
        return False
    
    def record_activity(self, activity_data):            
        activity = Activity(user=self, **activity_data)
        activity.save()
        
    @property
    def has_verification_request(self):
        return self.verification_request.all().exists()
    
    @property
    def verification_request_obj(self):
        last_request = self.verification_request.all().first()
        return last_request        
        
        
    @property
    def has_approved(self):
        return self.verification_request.filter(status__title__iexact = 'approved').exists()
    
    @property
    def has_rejected(self):
        return self.verification_request.filter(status__title__iexact = 'rejected').exists()
    
    @property
    def has_modified(self):
        return self.verification_request.filter(status__title__iexact = 'modified').exists()
    
    @property
    def has_pending(self):
        return self.verification_request.filter(status__title__iexact = 'pending').exists()
    
    @property
    def get_expert_profiles(self):
        all_expert_profiles = self.expert_profiles.all()
        return [profile for profile in all_expert_profiles if profile.has_approved]
    
    
    
class UserVerificationRequest(models.Model):
    ID_UPLOAD_TO = 'verification_id/'
    ADDRESS_UPLOAD_TO = 'verification_address/'
    
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="verification_request", unique=False)   
    id_proof = models.FileField(
        upload_to=ID_UPLOAD_TO,
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])]
    )
    address_proof = models.FileField(
        upload_to=ADDRESS_UPLOAD_TO,
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])]
    )
    status = models.ForeignKey(ApprovalStatus, on_delete=models.CASCADE, related_name="verification_approvals", default=ApprovalStatus.objects.get(title = 'pending').id, unique=False)
    office_remarks = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f'{self.user}--{self.status}'       

    
    @property
    def is_approved(self):
        return True if self.str_status == 'approved' else False
    
    @property
    def is_rejected(self):
        return True if self.str_status == 'rejected' else False
    
    @property
    def is_modified(self):
        return True if self.str_status == 'modified' else False
    
    @property
    def is_pending(self):            
        return True if self.str_status == 'pending' else False
        
    
    @property
    def colored_status(self):
        if self.is_approved:
            return '<span class="text-success">approved</span>'
        elif self.is_rejected:
            return '<span class="text-danger">rejected</span>'
        elif self.is_modified:
            return '<span class="text-danger">modified</span>'
        elif self.is_pending:
            return '<span class="text-warning">pending</span>'
        else:
            return 'UNKNOWN'
            
        
    @property
    def str_status(self):
        if self.status:
            return self.status.title.lower()
        
    def save(self, *args, **kwargs):   
        if not self.pk:
            if self.id_proof:
                self.id_proof.name = f"{self.user_id}-id_proof.{self.id_proof.name.split('.')[-1]}"
            if self.address_proof:
                self.address_proof.name = f"{self.user_id}-address_proof.{self.address_proof.name.split('.')[-1]}"            
        super().save(*args, **kwargs)
        
        
    
class GatewayReference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gateway_references')
    gateway = models.CharField(max_length=250, unique=True)
    reference = models.CharField(max_length=252)
    
    
         
        
    
class CustomResizeToFill(Resize):
    def process(self, img):
        if self.height is None:
            self.height = img.height

        if self.width is None:
            self.width = img.width

        img.thumbnail((self.width, self.height), Image.BICUBIC)

        return img

    
class Profile(models.Model):
    # It is beeing created autometically during signup by using signal.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    avatar = ProcessedImageField(upload_to='profile_photo',
                    processors=ProcessorPipeline([CustomResizeToFill(200, 200)]),
                    format='JPEG',
                    options={'quality': 60}, blank=True, null=True)
    about = models.TextField('About Me', max_length=500, blank=True, null=True)
    
    
    location = models.CharField('My Location', max_length=30, blank=True, null=True)
    birthdate = models.DateField(null=True, blank=True)    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)  
    
    def __str__(self):
        return 'Profile for ' +  str(self.user.email)  
    



class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_addresses')
    
    # Add address fields
    name = models.CharField(max_length=120)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    phone = PhoneNumberField('Address Phone', blank=True, null=True)
    country = CountryField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.name} - {self.phone} - {self.street_address} - {self.city} - {self.country}'
    
class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    ac_type = models.CharField(max_length=20)
    app_label = models.CharField(max_length=90)
    app_model = models.CharField(max_length=50)
    human_readable = models.CharField(max_length=150)
    description = models.TextField()
    path = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f'{self.ac_type} {self.human_readable}'
    
class Skill(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return f'{self.name}'
    
class ExpertType(models.Model):
    title = models.CharField(max_length=100)
    
    def __str__(self):
        return f'{self.title}'
    
    
    

class ExpertiesProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expert_profiles")
    title = models.CharField(max_length=250)
    expert_type = models.ForeignKey(ExpertType, on_delete=models.CASCADE, related_name="profile_of_expert_type")
    skills = models.ManyToManyField(Skill, related_name='expert_profile_of_skills')
    experience_years = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    

    
    
    
    def __str__(self):        
        skills_str = ', '.join([skill.name for skill in self.skills.all()])
        return f'{self.user} - {self.expert_type}({self.experience_years} years) - Skills: {skills_str}'
    
    @property
    def has_approved(self):
        return self.expertise_profile_approval_request.filter(status__title__iexact = 'approved').exists()
    
    @property
    def has_rejected(self):
        return self.expertise_profile_approval_request.filter(status__title__iexact = 'rejected').exists()
    
    @property
    def has_modified(self):
        return self.expertise_profile_approval_request.filter(status__title__iexact = 'modified').exists()
    
    @property
    def has_pending(self):
        return self.expertise_profile_approval_request.filter(status__title__iexact = 'pending').exists()
    


    
    @property
    def status(self):        
        if self.has_approved:            
            return '<span class="text-success">approved</span>'
        elif self.has_rejected:
            return '<span class="text-danger">rejected</span>'
        elif self.has_modified:
            return '<span class="text-danger">modified</span>'
        else:
            return '<span class="text-warning">pending</span>'
        
        

    
class ExpertProfileApprovalRequest(models.Model):
    expert_profile = models.ForeignKey(ExpertiesProfile, on_delete=models.CASCADE, related_name="expertise_profile_approval_request", unique=False)
    doc_title = models.CharField(max_length=150)
    suporting_doc = models.FileField(
        upload_to='approval_request_files/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])]
    )
    suporting_url = models.URLField(null=True, blank=True)
    description = models.TextField(max_length=500, null=True, blank=True)
    status = models.ForeignKey(ApprovalStatus, on_delete=models.CASCADE, related_name="experties_approvals", default=ApprovalStatus.objects.get(title = 'pending').id, unique=False)
    office_remarks = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    
    @property
    def is_approved(self):
        return True if self.str_status == 'approved' else False
    
    @property
    def is_rejected(self):
        return True if self.str_status == 'rejected' else False
    
    @property
    def is_modified(self):
        return True if self.str_status == 'modified' else False
    
    @property
    def is_pending(self):
        return True if self.str_status == 'pending' else False
    
    @property
    def colored_status(self):
        if self.is_approved:
            return '<span class="text-success">approved</span>'
        elif self.is_rejected:
            return '<span class="text-danger">rejected</span>'
        elif self.is_modified:
            return '<span class="text-danger">modified</span>'
        elif self.is_pending:
            return '<span class="text-warning">pending</span>'
        else:
            return 'UNKNOWN'
        
    @property
    def str_status(self):
        if self.status:
            return self.status.title.lower()        
        
    
    def save(self, *args, **kwargs):   
        if not self.pk:
            if self.suporting_doc:
                self.suporting_doc.name = f"{self.expert_profile.id}-{self.doc_title}--approval_doc.{self.suporting_doc.name.split('.')[-1]}"      
        super().save(*args, **kwargs)
    
    def __str__(self):        
        return f'{self.expert_profile.user}--{self.expert_profile}--{self.str_status}'   
    
    



    
         