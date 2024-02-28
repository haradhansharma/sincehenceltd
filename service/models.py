from datetime import datetime, timedelta
import random
import time
from django.contrib import messages
from django.conf import settings
from django.db import models
from django.urls import reverse
import uuid
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill, Resize, ProcessorPipeline
# from accounts.models import ExpertiesProfile
from accounts.models import *
from calendar_app.models import OffDay, WeekendDay
from service.helpers import get_project_created
from shcurrency.models import Currency
from PIL import Image
from django.core.validators import FileExtensionValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
from django.db.models import Count, Q, F
from django.utils import timezone

import logging
log =  logging.getLogger('log')

class ServiceCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    title = models.CharField(max_length=252, db_index=True)   
    banner = models.ImageField(upload_to='service/category_banner')
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    
    def get_absolute_url(self):
        return reverse('service:service_list') + f'?q={self.id}'
    
    def __str__(self):
        return self.title
    
    

class Service(models.Model):    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    categories = models.ManyToManyField(ServiceCategory, related_name="category_services")
    name = models.CharField(max_length=252, db_index=True)   
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    
    def get_absolute_url(self):
        return reverse('service:service_details', args=[str(self.pk)])
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-updated_at']
        
class CustomResizeToFill(Resize):
    def process(self, img):
        if self.height is None:
            self.height = img.height

        if self.width is None:
            self.width = img.width

        img.thumbnail((self.width, self.height), Image.BICUBIC)

        return img
    
class ServiceImage(models.Model):

    service = models.ForeignKey(Service, related_name='service_images', db_index=True, on_delete=models.CASCADE)
    picture = ProcessedImageField(
        upload_to='product_photo',
        processors=ProcessorPipeline([CustomResizeToFill(600, 600)]),
        format='JPEG',
        options={'quality': 70}
        )  
    
    def __str__(self):
        return self.service.name  
    
class ServiceMeta(models.Model):
    service = models.ForeignKey(Service, related_name='service_meta_data', db_index=True, on_delete=models.CASCADE)
    key = models.CharField(max_length=252)
    data = models.TextField()
    
    def __str__(self):
        return  f' ({self.service.name}) {self.data}'
    
class ServiceFeature(models.Model):
    service = models.ForeignKey(Service, related_name='service_features', db_index=True, on_delete=models.CASCADE)
    data = models.TextField()
    
    def __str__(self):
        return  f' ({self.service.name}) {self.data}'
   
        
class Quotation(models.Model): 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)     
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quotation_creator')
    reference_service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='quotation_reference')
    name = models.CharField(
        max_length=150, 
        help_text="Provide a nice title within 150 characters that will be displayed throughout the project's lifetime.", 
        verbose_name="Write a suitable title for your custom requirements")
    explanations = models.TextField(
        max_length=1200, 
        help_text="Write your project description or custom requirements within 1200 characters to help our team provide you with a comprehensive quotation based on your specific needs. Feel free to mention any reference links, specific work requirements, or preferred technology stack. Please ensure that your input is relevant to the referencing service on this page.",
        verbose_name="Your specific needs")
    require_by = models.DateTimeField(verbose_name="Quotation required by")    
    status = models.CharField(
        max_length=20, 
        choices=settings.QUOTATION_STATUS, 
        default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    
    
    class Meta:    
        ordering = ['-created_at'] 
    
    def __str__(self):
        return str(self.name)
    
    def get_absolute_url(self):
        return reverse("shop:web_quotation", args=[self.pk])
    
class QuotationData(models.Model):
    quotation = models.OneToOneField(Quotation, primary_key=True, on_delete=models.CASCADE, related_name='quotation_data')
    quotation_number = models.CharField(max_length=20, unique=True, editable=False)
    header = models.CharField(max_length=20)
    memo = models.TextField(max_length=400)
    footer = models.CharField(max_length=250)
    valid_till = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    
    
    
    def save(self, *args, **kwargs):
        # Generate the unique quotation number with a prefix.
        if not self.quotation_number:
            # Define your prefix here, for example, "QTN-"
            prefix = "QTN-"
            
            # Find the latest quotation number in the database.
            latest_quotation_data = QuotationData.objects.all().order_by('-created_at').first()
            
            try:
                # Extract the numeric part of the latest quotation number.
                numeric_part = int(latest_quotation_data.quotation_number[len(prefix):])               
                
                # Increment the numeric part.
                new_numeric_part = numeric_part + 1
                
                # Create the new quotation number with the prefix and incremented numeric part.
                self.quotation_number = f"{prefix}{new_numeric_part:04d}"
            except Exception as e:
                # print(e)
                # If there are no existing quotations, start with "QTN-0001."
                self.quotation_number = f"{prefix}0001"
        
        super().save(*args, **kwargs)
        
class QuotationToDo(models.Model):
    quotation = models.ForeignKey(Quotation, related_name='quotation_todo', db_index=True, on_delete=models.CASCADE)
    data = models.CharField(
        max_length=252, 
        help_text="Outline to do it will be added to the order text. " 
        )
    can_edit_by_customer = models.BooleanField(default=False)
    
    
    
        
class Price(models.Model):
    PRICE_TYPES = settings.PRICE_TYPES
    INTERVAL = settings.INTERVAL
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)     
    service = models.ForeignKey(Service, related_name='prices_of_service', null=True, blank=True, db_index=True, on_delete=models.CASCADE)
    quotation = models.OneToOneField(Quotation, related_name='prices_of_quotation', null=True, blank=True, db_index=True, on_delete=models.CASCADE)    
    name = models.CharField(max_length=252, db_index=True)   
    features = models.TextField()
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    currency = models.ForeignKey(Currency, related_name='currency_of_price', db_index=True, on_delete=models.CASCADE)
    price_type = models.CharField(choices=PRICE_TYPES, null=True, blank=True, max_length=100, db_index=True)
    interval = models.CharField(choices=INTERVAL, null=True, blank=True, max_length=100, db_index=True, help_text="Use as recurring interval for suscription or require time for one time price")
    interval_count = models.IntegerField(default=1)   
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    
    def __str__(self):        
        return self.price_for_obj
    
    
    
    @property
    def is_service(self):
        if self.service is not None:
            return True
        return False
    
    @property
    def is_quotation(self):
        if self.quotation is not None:
            return True
        return False
    
    @property
    def price_for_obj(self):
        if self.is_service:
            service_or_quotation_title = self.service.name
            obj = 'Service'
        elif self.is_quotation:
            service_or_quotation_title = self.quotation.name
            obj = 'Quotation'
        else:
            service_or_quotation_title = ''
            obj =''           
    
        return f'"{self.name}" of {obj} "{service_or_quotation_title}"'
    
    @property
    def resume_url(self):
        if self.is_service:
            service_or_qutation_id = self.service.id
        elif self.is_quotation:
            service_or_qutation_id = self.quotation.id      
        else:
            service_or_qutation_id = ''
            
        return reverse('service:collect_order_info', args=[service_or_qutation_id, self.id])
    
    @property
    def is_onetime(self):
        if self.price_type == 'one_time':
            return True
        return False
    
    @property
    def is_subscription(self):
        if self.price_type == 'recurring':
            return True
        return False
    
    
    
    def save(self, *args, **kwargs):
        # Check if both service and quotation are set
        if self.service and self.quotation:
            log.warning('Someone tried to add service and quotation at the same time!______')
            raise ValidationError("You cannot set both 'service' and 'quotation' at the same time.")
        super(Price, self).save(*args, **kwargs)
        
        


class Order(models.Model): 
    STATUS = settings.ORDER_STATUS    
 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)    # client_reference_id
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    price = models.ForeignKey(Price, related_name='orders_price', on_delete=models.CASCADE, null=True, blank=True) 
    
    currency = models.ForeignKey(Currency, related_name='order_currency', null=True, blank=True, db_index=True, on_delete=models.CASCADE)
    amount = models.FloatField()
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders', null=True, blank=True, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS, default='pending', max_length=100, db_index=True) 
       
    gateway_reference = models.TextField(null=True, blank=True) # checkout session id
    gateway_reference2 = models.TextField(null=True, blank=True) # subscription id
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    tentative_delivery = models.DateTimeField(null=True, blank=True)    
    
    subscription_active = models.BooleanField(default=False) # use only for subscriptio product
    subscription_pushed = models.BooleanField(default=False) # use only for subscriptio product     
    
    gateway_payment_url = models.TextField(null=True, blank=True)
    last_followup_on = models.DateTimeField(null=True, blank=True) 
    total_followup = models.IntegerField(default=0)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    
    class Meta:    
        ordering = ['-created_at']         

        
    def save(self, *args, **kwargs):
        current_year = datetime.now().year % 100         
        if not self.order_number:
            # Define your prefix here, for example, "QTN-"
            if self.price.is_service:
                prefix = "ORSRV-"
            elif self.price.is_quotation:
                prefix = "ORQTN-"
            
            # Find the latest quotation number in the database.
            latest_order = Order.objects.all().order_by('-created_at').first()
            
            try:
                # Extract the numeric part of the latest quotation number.
                numeric_part = int(latest_order.order_number.split('/')[0][len(prefix):])               
                print(numeric_part)
                # Increment the numeric part.
                new_numeric_part = numeric_part + 1
                
                # Create the new quotation number with the prefix and incremented numeric part.
                self.order_number = f"{prefix}{new_numeric_part:06d}/{current_year:02d}"
            except Exception as e:
                print(e)
                # If there are no existing quotations, start with "QTN-0001."
                self.order_number = f"{prefix}000001/{current_year:02d}"
        
        super().save(*args, **kwargs)
    
    # @property
    # def is_allowed_to_checkout(self):
    #     allowed_status_to_collect_info  = settings.ALLOED_STATUS_TO_CHECKOUT        
    #     if self.status in allowed_status_to_collect_info:           
    #         return True              
    #     return False 
    
    # @property
    # def is_pending(self):
    #     if self.status in settings.ALLOED_STATUS_TO_CHECKOUT:
    #         return True
    #     return False   
    
    def get_absolute_url(self):
        return reverse("accounts:order", kwargs={"pk": self.pk}) 
        
    @property
    def get_checkout_url(self):
        pk1 = self.price.service.pk if self.price.is_service else self.price.quotation.pk
        pk2 = self.price.pk        
        return reverse('service:collect_order_info', args=[self.id, pk1, pk2])    
    
    # @property
    # def inv(self):
    #     try:
    #         invoice = self.invoice        
    #     except Exception as e:
    #         invoice = None
            
    #     return invoice
    
    @property
    def trans_amount(self):
        total_amount = self.order_trans.filter(check_and_confirmed = True).aggregate(total=Sum('amount'))['total']     
        if total_amount is not None:     
            t_amount = total_amount
        else:
            t_amount = 0
     
        return t_amount
    
    @property
    def pending_amount(self):
        result = self.amount - self.trans_amount
  
        return max(result, 0)
    
    @property
    def trans_reject_amount(self):
        total_amount = self.order_trans.filter(check_and_reject = True).aggregate(total=Sum('amount'))['total']     
        if total_amount is not None:     
            t_amount = total_amount
        else:
            t_amount = 0
     
        return t_amount
    
    @property
    def trans_checking_amount(self):
        total_amount = self.order_trans.filter(check_and_reject = False, check_and_confirmed = False).aggregate(total=Sum('amount'))['total']     
        if total_amount is not None:     
            t_amount = total_amount
        else:
            t_amount = 0
     
        return t_amount
    
    
    @property
    def has_transactions(self):
        return self.order_trans.all().exists()
    
    @property
    def has_project(self):
        if hasattr(self, 'order_project'):
            return True
        return False
 
    
    
    def __str__(self):
        # title = self.price.service.name if self.price.is_service else self.price.quotation.name
        return self.order_number
    


class OrderText(models.Model):
    order = models.ForeignKey(Order, related_name='order_req_texts', db_index=True, on_delete=models.CASCADE)
    data = models.CharField(
        max_length=252, 
        help_text="Please add your to-do items here if you have already outlined it. " 
        "If it aligns with our workflow, we will keep it as is; otherwise, we may edit it to meet your project requirements. " 
        "Each line can contain up to 252 characters here. " 
        "Click the 'Add More Line' button if you need more lines.")
    
    def __str__(self):
        return self.data
    
class OrderFile(models.Model):
    order = models.ForeignKey(Order, related_name='order_req_files', db_index=True, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to='private_dir/order_files/',      
        null=True,
        blank=True,
        help_text="Please upload your project requirements in detail. We accept PDF files, with a maximum file size of 5 MB per file." 
        " If your file is larger, consider splitting it. Uploaded requirements carry significant weight, but if any part is unclear, "
        "we will discuss it in our ongoing discussions, and strict adherence may not be possible in such cases"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
class OrderImage(models.Model):
    order = models.ForeignKey(Order, related_name='order_req_images', db_index=True, on_delete=models.CASCADE)
    images = models.ImageField(
        upload_to='private_dir/order_images/',        
        null=True,
        blank=True,
        help_text="If you have any reference images for the project, you may include them with your order for consideration. 1 MB limit per file. Please note that it is not recommended, and we cannot guarantee strict adherence to reference images."
        
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    
class OrderInvoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, primary_key=True, related_name="invoice")
    filepath = models.FileField(upload_to=settings.INVOICE_UPLOAD_TO)
    validity = models.DateTimeField()
    gateway = models.CharField(max_length=50, default='')
    due = models.BooleanField(default=True)    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.order}'
    
    @property
    def update_payment_url(self):
        return reverse('service:update_payment', args=[self.order.id])
    
    @property
    def cancel_order_url(self):
        return reverse('service:cancel_order', args=[self.order.id])
    
    
    def should_delete(self):
        if self.order.status in settings.PAYMENT_PENDING_STATUS and not self.order.has_transactions and self.validity < timezone.now():
            return True
        return False
  
    
    
class OrderTransaction(models.Model):
    '''
    all transaction checked manually
    '''
    STATUS = settings.PAYMENT_STATUS
    # TRANSACTION_TYPE = settings.TRANSACTION_TYPE
    TRANSACTION_FOR = settings.TRANSACTION_FOR
    
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.CASCADE, related_name='order_trans')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='customer_trans', on_delete=models.CASCADE)
    # item_title = models.CharField(max_length=250, null=True, blank=True)
    # price_title = models.CharField(max_length=250, null=True, blank=True)    
    trxID = models.TextField()  
    # trans_for = models.CharField(choices=TRANSACTION_FOR, null=True, blank=True, max_length=100, db_index=True)    
    status = models.CharField(choices=STATUS, null=True, blank=True, max_length=100, db_index=True)
    gateway = models.CharField(max_length=20, null=True, blank=True)
    # gateway_reference = models.TextField(null=True, blank=True) # payment intent if stripe
    # gateway_invoice = models.TextField(max_length=150, null=True, blank=True) 
    # amount_subtotal = models.FloatField(default=0)
    amount = models.FloatField(default=0)       
    paymemt_currency = models.ForeignKey(Currency, related_name='trans_currency', null=True, blank=True, db_index=True, on_delete=models.CASCADE)
    # autoamtic_tax = models.CharField(max_length=150, null=True, blank=True)
    
    mobile = models.CharField(max_length=50, null=True, blank=True)
    check_and_confirmed = models.BooleanField(default=False)
    check_and_reject = models.BooleanField(default=False)
    
    screenshoot = models.FileField(
        upload_to='transactions/screenshoot', 
        validators=[ 
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'pdf'], message='Only image (jpg, jpeg, png, gif) and PDF files are allowed.')
            ]
        )
    
    remarks = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True) 
    
    def __str__(self):        
        return f'Transaction of {self.customer.username}' 
    
    def save(self, *args, **kwargs):
        
        request = kwargs.pop('request', None)
       
        if self.pk:            
            old_obj = OrderTransaction.objects.get(pk=self.pk)
            
            if old_obj.check_and_confirmed and self.check_and_reject:
                messages.error(request, 'It is already confirmed! So can not changed!') # Later this validation will changed to if project created!
                return
            
            if self.check_and_confirmed:
                self.order.status = settings.PAYMENT_CONFIRM_STATUS
            elif self.check_and_reject:
                self.order.status = settings.PAYMENT_REJECT_STATUS
            self.order.save()
        
        if self.order and self.paymemt_currency != self.order.currency:
            messages.error(request, "Payment currency does not match the order's currency")
            return
            # raise ValidationError("Payment currency does not match the order's currency")
        
        super().save(*args, **kwargs)
    
class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    order = models.OneToOneField(Order, null=True, blank=True, on_delete=models.CASCADE, related_name='order_project')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True) 
    
    def __str__(self):
        return f'{self.id}-{self.order.order_number}-{self.order.price}'
    
    @property
    def contributors(self):
        return self.project_contributors.all()
    
    @property
    def contributing_users(self):
        return list(set(c.contributor.user for c in self.contributors))
    
    @property
    def customer_and_team(self):
        return [self.order.customer]
    
class ProjectContributor(models.Model):         
    project = models.ForeignKey(Project, related_name='project_contributors', on_delete=models.CASCADE)
    contributor = models.ForeignKey(ExpertiesProfile, on_delete=models.CASCADE, related_name='contributing_to', limit_choices_to={'expertise_profile_approval_request__status__title__iexact':'approved'})
    task_type = models.ManyToManyField(ExpertType, related_name='contributors_of_expertise')    
    
    def __str__(self):
        return f'{self.contributor} for project {self.project}'
    

    
class ProjectTodo(models.Model): 
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_todo")
    milestone = models.TextField(max_length=300)
    description = models.TextField()    
    required_days = models.IntegerField()
    target_date = models.DateTimeField(null = True, blank = True)
    miltstone_type = models.ForeignKey(ExpertType, on_delete=models.CASCADE, max_length=100, db_index=True, related_name="type_todos")
    sort_order = models.IntegerField()
    reference = models.ForeignKey(OrderText, on_delete=models.CASCADE, related_name='ordertext_project_todo')
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def contributors(self):
        all_contributors_of_project = self.project.contributors
        contributors_of_this_todo = list(set(contributor for contributor in all_contributors_of_project if self.miltstone_type in contributor.task_type.all()))
        return contributors_of_this_todo
    
    @property
    def alowed_user_to_interactions(self):
        return list(set(c.contributor.user for c in self.contributors))
        
    
    def __str__(self):
        m_type = self.miltstone_type if self.miltstone_type is not None else ''
        return f'{self.milestone}({m_type})----{self.project}'
    
    class Meta:
        ordering = ('sort_order', )
        
    # @property
    # def total_required_days(self):        
    #     return self.project.project_todo.aggregate(total_days=Sum('required_days'))['total_days'] or 0
      
    @property  
    def target_to_finish(self):    
          
        project_created = get_project_created(self) 
        
        primary_finishdate = project_created + timezone.timedelta(days=self.required_days)        
        
        total_off_within_primary_finishdate = OffDay.objects.filter(
            selected_date__range=[project_created, primary_finishdate]
        ).count()      
  
        weekend_days = set(WeekendDay.objects.values_list('day_of_week', flat=True))
        
        total_weekend_days_within_primary_period = 0
        current_date = project_created
        while current_date <= primary_finishdate:           
            if current_date.weekday() in weekend_days:
                total_weekend_days_within_primary_period += 1
            current_date += timezone.timedelta(days=1)      
        
        final_finishdate = primary_finishdate + timezone.timedelta(days=total_off_within_primary_finishdate) + timezone.timedelta(days=total_weekend_days_within_primary_period)        
      
        return final_finishdate + timezone.timedelta(days=self.total_awaited)
    
    @property
    def next_todo(self):
        next_todo = ProjectTodo.objects.filter(
            project=self.project,
            sort_order__gt=self.sort_order
        ).order_by('sort_order').first()
        return next_todo

    @property
    def previous_todo(self):
        previous_todo = ProjectTodo.objects.filter(
            project=self.project,
            sort_order__lt=self.sort_order
        ).order_by('-sort_order').first()
        return previous_todo
    

    @classmethod
    def update_target_dates(cls, pk):
        todos = cls.objects.filter(project__pk = pk).order_by('sort_order')          
        for todo in todos:   
            todo.target_date =  todo.target_to_finish 
            todo.save()      
            
    @property
    def interactions(self):
        return self.todo_interactions.all()  
    
    @property
    def total_awaiting(self):
        total = 0
        for i in self.interactions:  
            if i.awaiting >= 0:
                total += i.awaiting           
        return total     
    
    @property
    def total_awaited(self):
        total = 0
        for i in self.interactions:
            if i.user_is_project_customer:
                total += int(i.waited_for_reply)
            else:
                continue
        
        return total

    
               
class Interactions(models.Model):
    todo = models.ForeignKey(ProjectTodo, on_delete=models.CASCADE, related_name = 'todo_interactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="contributor_interactions")    
    body = models.TextField()    
    ans_required = models.BooleanField('Answer Required', default=True)
    reply_accepted = models.BooleanField(default=False)
    waited_for_reply = models.IntegerField(default=0)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    
    class Meta:
        ordering = ('created_at', )
        
    @property
    def user_is_project_contributor(self):
        contributing_user = self.todo.project.contributing_users      
        if self.user in contributing_user:
            return True
        else:
            return False
        
    @property
    def user_is_project_customer(self):
        customers = self.todo.project.customer_and_team  
        if self.user in customers:
            return True
        else:
            return False        
    
    
    @property
    def next_interaction(self):
        ni = Interactions.objects.filter(
            todo = self.todo,
            created_at__gt = self.created_at
        ).order_by('created_at').first()

        return ni

    @property
    def previous_interaction(self):
        pi = Interactions.objects.filter(
            todo=self.todo,
            created_at__lt=self.created_at
        ).order_by('-created_at').first()
        return pi
    
    @property
    def has_ans_required_but_not_replied_in_previous(self):
        return Interactions.objects.filter(
                    todo=self.todo,
                    created_at__lt=self.created_at ,
                    ans_required=True,
                    reply_accepted=False          
                ).exists()
    
    @property
    def last_contributor_interaction(self):
        last_contributor_interaction = Interactions.objects.filter(
            todo=self.todo,
            user__in=self.todo.project.contributing_users,
            ans_required=True,
            reply_accepted=False
        ).order_by('created_at').last()
        
        return last_contributor_interaction
        
    
    @property
    def customer_after_dev(self):
        # Get the last interaction of contributing users
        last_contributor_interaction = self.last_contributor_interaction

        # Check if there is a last contributor interaction
        if last_contributor_interaction:
            # Check if there are customer interactions after the last contributor interaction
            has_customer_interactions_after = Interactions.objects.filter(
                created_at__gt=last_contributor_interaction.created_at,
                user__in=self.todo.project.customer_and_team           
            ).exists()
            return has_customer_interactions_after
        else:
            return False
    
    @property
    def awaiting(self):      
        
        if self.ans_required:
            if self.reply_accepted:
                print(f'-returning 0 if reply accepted')
                return 0
            elif not self.reply_accepted:
                print(f'-entered into if not reply accepted')
                if not self.customer_after_dev or not self.next_interaction or (self.next_interaction and self.next_interaction.user in self.todo.project.contributing_users):
                    print(f'--entered into if customer after dev and next user is in dev')
                    waiting = timezone.now() - self.last_contributor_interaction.created_at      
                    waiting_hours = waiting.total_seconds() // 3600 # convert to hours     
                    if int(waiting_hours) >= 24:      
                        print(f'---return as it is more then 24')          
                        return int(waiting_hours) // 24 # convert to days
                    else:
                        print(f'---return 0 as it is less then 24')    
                        return 0    
                else:
                    print(f'-returning 0 as has customer after dev')
                    return 0      
        else: 
            print(f'returning 0 as ans is not required')       
            # if self.user in self.todo.project.contributing_users:
            #     return 0
            return 0


    