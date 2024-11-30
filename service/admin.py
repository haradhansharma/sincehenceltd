from django.conf import settings
from django.contrib import admin , messages
from django.core.mail import send_mail
from django.http import HttpResponse
from core.helper import custom_send_mass_mail
from core.tasks import send_mass_mail_task
from .models import *
from.forms import *
from django.core.exceptions import ValidationError
from django import forms
from django.forms.models import BaseInlineFormSet

import logging
log =  logging.getLogger('log')

class ServiceCategoryAdmin(admin.ModelAdmin):  
      
    list_display = ('title',)   
 
admin.site.register(ServiceCategory)

class ServiceImagesInline(admin.TabularInline):    
    model = ServiceImage
    extra = 0
    fk_name = "service"   

class ServiceMetaInline(admin.TabularInline):    
    model = ServiceMeta
    extra = 0
    fk_name = "service"   
    
class ServiceFeaturesInline(admin.TabularInline):    
    model = ServiceFeature
    extra = 0
    fk_name = "service" 
    
class PriceInline(admin.StackedInline):    
    model = Price
    extra = 0
    fk_name = "service"  
    form = PriceAdminForm    

    
class ServiceAdmin(admin.ModelAdmin):  
      
    inlines = [ServiceImagesInline, ServiceMetaInline, ServiceFeaturesInline, PriceInline]    
 
admin.site.register(Service, ServiceAdmin)



class QuotationDataInlineFormSet(BaseInlineFormSet):
    
    def clean(self):
        # Initialize a flag to track whether any form has data.
        has_data = False

        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                # Check if any relevant fields in the form have data.
                if form.cleaned_data.get('quotation') or form.cleaned_data.get('header'):
                    has_data = True
                    break

        # If no form has data, raise a validation error.
        if not has_data:
            raise forms.ValidationError("Quotation data must have.")
        
class QuotationPriceInlineFormSet(BaseInlineFormSet):
    def clean(self):
        # Initialize a flag to track whether any form has data.
        has_data = False

        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                # Check if any relevant fields in the form have data.
                if form.cleaned_data.get('quotation') or form.cleaned_data.get('name'):
                    has_data = True
                    break

        # If no form has data, raise a validation error.
        if not has_data:
            raise forms.ValidationError("Quotation price must have.") 
        

class QuotationDataInline(admin.TabularInline):
    model = QuotationData
    can_delete = False   
    formset = QuotationDataInlineFormSet
    
class QuotationPriceInline(admin.TabularInline):
    model = Price
    can_delete = False  
    exclude = ['service']
    formset = QuotationPriceInlineFormSet  
    
class QuotationToDoInline(admin.TabularInline):
    model = QuotationToDo
    max_num = 12
   

class QuotationAdmin(admin.ModelAdmin):
    list_display = ('name', 'require_by', 'status', 'created_at', 'quotationdata_valid_till')   
    list_filter = ['id', 'creator']
    search_fields = ['name']
    readonly_fields = ('creator', 'reference_service', ) 
    inlines = [QuotationDataInline, QuotationPriceInline, QuotationToDoInline]   
    
    @admin.display(description='Valid Till')
    def quotationdata_valid_till(self, obj):
        return obj.quotation_data.valid_till
    
    class Media:
        css = {
            'all': (
                '/static/assets/css/custom_admin.css',
            )
        } 
         
    
    ####### Added extra butoon
    change_form_template = "admin/quotationrequest_change_form.html"  
    
    
    #### Ading information abot not setup Quotation Data and Quotation Price!
    change_list_template = 'admin/quotation_list.html'
    
    def changelist_view(self, request, extra_context=None):  
            
        open_quotations = Quotation.objects.filter(status = 'open')          
        setup_pending = []
        for quotation in open_quotations:
            if hasattr(quotation, 'quotation_data') and hasattr(quotation, 'prices_of_quotation'):
                pass
            else:
                setup_pending.append(quotation.name)   
                 
        extra_context = extra_context or {}
        extra_context['setup_pending'] = setup_pending      
          
        return super().changelist_view(request, extra_context=extra_context)  
    
    
    def response_add(self, request, obj, post_url_continue=None):    
        if "_send_email" in request.POST:
            self.send_email(request, None, obj) 
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):        
        if "_send_email" in request.POST:
            self.send_email(request, None, obj)
        return super().response_change(request, obj)
    
    def get_message(self, request, obj):
        message = f"Dear {obj.creator.get_full_name() or obj.creator.username},\n\nWe hope this message finds you well. Thank you for considering SINCEHENCE LTD for your custom service requirements." 
        message += f"We are pleased to provide you with the quotation you requested.\n\n"
        message += f"You can review the quotation details by clicking on the link below:\n\n"
        message += f"{request.build_absolute_uri(obj.get_absolute_url())}\n\n"
        message += f"[Note: The provided link will take you to a secure webpage where you can view the quotation, accept or reject the offer, and proceed to our payment gateway for your convenience. Additionally, you can download the quotation as a PDF for your records.]\n\n"
        message += f"We have taken into account all your specific requirements and have tailored this quotation to best suit your needs. If you have any questions, need further clarification, or wish to discuss any aspect of the quotation, please feel free to contact us.\n\n"
        message += f"We value your business and look forward to the possibility of serving you. Your satisfaction is our priority, and we are committed to providing the highest level of service.\n\n"
        message += f"Thank you for considering SINCEHENCE LTD, and we hope to hear from you soon.\n\n\n\n"
        message += f"Best regards,\n\n"
        message += f"SINCEHENCE TEAM\n\n"  
        
        return message
    
    @admin.action(description='Send quotation to the creator of the selected Quotation request.')
    def send_email(self, request, queryset = None, obj = None):
       
        from_email = settings.DEFAULT_FROM_EMAIL     
        email_messages = []              
        
        if queryset is not None:                
            for obj in queryset:
                ### VERY IMPORTANT
                # print(hasattr(obj, 'quotation_data'))
                # print(hasattr(obj, 'prices_of_quotation'))
                
                if hasattr(obj, 'quotation_data') and hasattr(obj, 'prices_of_quotation'):
                    obj.status = 'response_sent'   
                    obj.save()                
                    subject = f"SINCEHENCE LTD - Offered you a quotation for {obj.name.upper()}!" 
                    message = self.get_message(request, obj)                              
                    email_messages.append((subject, message, from_email, [obj.creator.email] , '',  ['info@sincehence.co.uk'], ''))      
                else:
                    log.warning(f'Quotation data and Quotation price setup pending in "{obj.name}". Mail can not sent!!')
                    messages.warning(request, f'Quotation data and Quotation price setup pending in "{obj.name}". Mail can not sent!!')         
        
        elif obj is not None:  
            ### VERY IMPORTANT 
            # print(hasattr(obj, 'quotation_data'))
            # print(hasattr(obj, 'prices_of_quotation'))
            if hasattr(obj, 'quotation_data') and hasattr(obj, 'prices_of_quotation'):
                obj.status = 'response_sent'   
                obj.save()
                subject = f"SINCEHENCE LTD - Offered you a quotation for {obj.name.upper()}!" 
                message = self.get_message(request, obj)                               
                email_messages.append((subject, message, from_email, [obj.creator.email] , '',  ['info@sincehence.co.uk'], ''))  
            else:
                log.warning(f'Quotation data and Quotation price setup pending in "{obj.name}". Mail can not sent!!')
                messages.warning(request, f'Quotation data and Quotation price setup pending in "{obj.name}". Mail can not sent!!')   
        else:
            pass
        
        if len(email_messages) > 0:    
            send_mass_mail_task.delay(email_messages, fail_silently=False)
            # custom_send_mass_mail(email_messages, fail_silently=False)
        
    actions = [send_email] 
    
admin.site.register(Quotation, QuotationAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'price', 'currency', 'amount', 'customer', 'status', 'created_at', 'order_project')   
    list_filter = ['order_number', 'customer', 'status']
    # search_fields = ['name']
    readonly_fields = ('order_number', 'customer','total_followup','last_followup_on','currency','amount', 'status','price',) 
    
    
    
    @admin.action(
        permissions=["change"],
        description="Create project",
    )
    def create_project(self, request, queryset):
        print('action called successfully')
        
        
        confirmed_orders = queryset.filter(status=settings.PAYMENT_CONFIRM_STATUS)
    
        projects_to_create = [
            Project(order=order) for order in confirmed_orders if not order.has_project
        ]

        created_count = len(Project.objects.bulk_create(projects_to_create))
        self.message_user(request, f"Successfully created {created_count} projects by considering order status is '{settings.PAYMENT_CONFIRM_STATUS}' and have no project created!")
                
        
                
            
    
    
    actions = [create_project] 
    
admin.site.register(Order, OrderAdmin)

class OrderTransactionAdmin(admin.ModelAdmin):
   
    def save_model(self, request, obj, form, change):   
        '''
        everything do here. do not call super().save as it will cause reduant.
        '''
        obj.save(request=request)
       
    
admin.site.register(OrderTransaction, OrderTransactionAdmin)

class OrderInvoiceAdmin(admin.ModelAdmin):
    pass
    
admin.site.register(OrderInvoice, OrderInvoiceAdmin)



class ProjectTodoInline(admin.TabularInline):
    model = ProjectTodo 
    extra = 1
    fk_name = 'project'     
    readonly_fields = ('target_date', ) 
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'reference':      
            parent_model_instance = self.parent_model.objects.get(pk=request.resolver_match.kwargs['object_id'])
            if isinstance(parent_model_instance, Project):
                current_project = parent_model_instance
                kwargs["queryset"] = current_project.order.order_req_texts.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    

     

    
class ProjectContributorInline(admin.TabularInline):
    model = ProjectContributor

    extra = 1
    fk_name = 'project'
    list_display = ('contributor', 'for_task_of', )
 
    

class ProjectAdmin(admin.ModelAdmin):

    change_form_template = "admin/project_change_form.html"  
    inlines = [ProjectTodoInline, ProjectContributorInline]    
    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # This gets triggered after saving the inline form
        instance = form.instance
        ProjectTodo.update_target_dates(instance.pk)
    
    
    def change_view(self, request, object_id, form_url="", extra_context=None):        
        
                 
        extra_context = extra_context or {}
        
        project = Project.objects.get(id = object_id)
        
        order_todos = project.order.order_req_texts.all()
        order_files = project.order.order_req_files.all()
        order_images = project.order.order_req_images.all()  
        
        
        
        extra_context['order_todos'] = order_todos
        extra_context['order_files'] = order_files   
        extra_context['order_images'] = order_images             
          
        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)    

    
admin.site.register(Project, ProjectAdmin)



class ProjectTodoAdmin(admin.ModelAdmin):
    pass
    
admin.site.register(ProjectTodo, ProjectTodoAdmin)

class InteractionsAdmin(admin.ModelAdmin):
    pass
    
admin.site.register(Interactions, InteractionsAdmin)
