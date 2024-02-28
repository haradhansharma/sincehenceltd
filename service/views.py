from datetime import datetime
from django.utils import timezone
import random
import string
from django.forms import formset_factory, inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView
from accounts.models import User
from core.agent_helper import get_location_info
from core.context_processor import site_data
from core.helper import converted_amount, calculate_delivery_date, user_activities
from core.templatetags.core import formatedprice, price_msg, title_and_price
from service.forms import  EmailCollectionForm, OrderFileForm, OrderImageForm, OrderTextForm, PaymentForm, PaymentGatewayForm, ServicePriceForm
from payment_method.gateways.base import PaymentGatewayBase
from .models import *
from django.views import View
from payment_method.gateways import active_payment_methods
import uuid
from payment_method.utils import get_payment_method_class
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import io
from django.http import FileResponse, Http404, HttpResponse, HttpResponseRedirect
from core.templatetags.core import convert_amount, formatedprice, get_user_identity, remove_dash_hyphen_capital
from service.forms import ServicePriceForm
from service.decorators import quotation_creator_required
from service.forms import AcceptForm, QuotationForm, RejectForm
from django.contrib.auth.mixins import LoginRequiredMixin
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch

import logging
log =  logging.getLogger('log')

class ServiceList(ListView):
    model = Service
    template_name = 'service/service_list.html'  # Replace with your desired template path
    context_object_name = 'services'  # This sets the variable name in the template
    paginate_by = 10  # Number of services to display per page (you can change this as needed)
    ordering = '-updated_at'
    
    def get_queryset(self):
        selected_category_id = self.request.GET.get('q', None)

        if selected_category_id is not None:
            selected_category_id = uuid.UUID(selected_category_id)
            category_obj = get_object_or_404(ServiceCategory, pk=selected_category_id)
            services_queryset = category_obj.category_services.filter(is_active=True).prefetch_related(
                'service_images',
                'service_meta_data',
                'service_features',
                'prices_of_service',
            )
        else:
            services_queryset = Service.objects.filter(is_active=True).prefetch_related(
                'service_images',
                'service_meta_data',
                'service_features',
                'prices_of_service',
            )

        return services_queryset

    def get_context_data(self, **kwargs):
        context = super(ServiceList, self).get_context_data(**kwargs)
        site = site_data()
        site['title'] = 'Our Services'
        site['description'] = 'Discover our top-tier services: Web Development, ERP Solutions, Graphic Design, API Integration, Payment Gateways, eCommerce Development, and Monthly Retainers. Your digital success, our expertise.'
        context['site_data'] = site
        
        service_categories = ServiceCategory.objects.filter(is_active=True)        
        context['service_categories'] = service_categories
        
        selected_category_id = self.request.GET.get('q', None)           
        if selected_category_id is not None:
            category_id = uuid.UUID(selected_category_id)    
        else:    
            category_id = selected_category_id
            
        context['filters'] = {'q' : [category_id]}
        context['q'] = category_id
        
        if settings.SALING_SERVICE:
            return context
        else:
            raise Http404
    

def get_formatted_prices(service, currency):    
    return [formatedprice(price, currency) for price in service.prices_of_service.all()]


class ServiceDetailView(View):
    http_method_names = ['get', 'post']
    template_name = 'service/service_detail.html'
    
    @property
    def service_id(self):
        service_id = self.kwargs['pk']
        return service_id

    @property
    def get_service(self):   
        return get_object_or_404(Service.objects.prefetch_related('prices_of_service'), pk=self.service_id)
    
    @property
    def get_formated_price(self):
        formatted_prices = get_formatted_prices(self.get_service, self.request.currency)
        return formatted_prices
    
    
    @property
    def default_context(self):
        context = {}
        
        site = site_data()
        site['title'] = self.get_service.name
        site['description'] = self.get_service.description[:150]        
        
        context['site_data'] = site
        context['service'] = self.get_service
        
        
        return context         
        

    def get(self, *args, **kwargs):        
        context = self.default_context  
         
        price_option_form = ServicePriceForm(
            prices=self.get_service.prices_of_service.all(), 
            formatted_prices=self.get_formated_price
            )    
        
        
        context['form'] = price_option_form  
        
        if settings.SALING_SERVICE:
            return render(self.request, self.template_name, context)
        else:
            raise Http404

    def post(self, *args, **kwargs):
        if settings.SALING_SERVICE:
            pass
        else:
            raise Http404
        
        context = self.default_context   
        
        price_option_form = ServicePriceForm(
            prices=self.get_service.prices_of_service.all(), 
            formatted_prices=self.get_formated_price, 
            data=self.request.POST
            )                    
        if price_option_form.is_valid():
            selected_price_id =  uuid.UUID(price_option_form.cleaned_data['price_id'])     
            price_obj = Price.objects.get(id = selected_price_id)                   
            return HttpResponseRedirect(price_obj.resume_url)
        else:
            messages.warning(self.request, 'Select valid price options!')
            return render(self.request, self.template_name, context)
        
class CollectOrderInfo(View):
    http_method_names = ['get', 'post']
    template_name = 'service/collect_order_info.html' 
    
    @property
    def service_id(self):
        return self.kwargs['service_id']
    
    @property
    def service(self):
        obj = get_object_or_404(Service, pk=self.service_id)
        return obj
    
    @property
    def selected_price_id(self):
        return self.kwargs['selected_price_id']
    
    @property
    def price_obj(self):
        obj = get_object_or_404(Price, pk=self.selected_price_id)
        return obj
    
    
    def get_valid_payment_gateways(self, amount):
        
        location_data = get_location_info(self.request)
        
        ip = location_data.get('ip')    
        if ip == '127.0.0.1':
            user_country = 'BD'
        else:
            user_country = location_data.get('country')
            
        payment_gateways = {}
        for payment_method in active_payment_methods:
            
            if isinstance(payment_method, PaymentGatewayBase): 
                allowed_amount_min, allowed_amount_max, allowed_amount_any = payment_method.allowed_amount()
                allowed_countries, allowed_any_country = payment_method.allowed_countries()
                # Check if the order amount is within the allowed range
                if allowed_amount_min <= amount <= allowed_amount_max or allowed_amount_any:
                    # Check if the user is browsing from an allowed country
                    if user_country in allowed_countries or allowed_any_country:  
                        payment_gateways[payment_method.get_gateway_name()] = payment_method.get_help_text()
            
                
        return payment_gateways
    
    def get_formsets(self):
        # Create formsets for related models
        OrderTextFormSet = formset_factory(OrderTextForm, extra=1, max_num=12, can_delete=False)
        OrderFileFormSet = formset_factory(OrderFileForm, extra=1, max_num=3, can_delete=False)
        OrderImageFormSet = formset_factory(OrderImageForm, extra=1, max_num=3, can_delete=False)
   
        if self.request.method == 'GET':
            order_text_forms = OrderTextFormSet(self.request.POST or None, self.request.FILES or None, prefix='order_text')
            order_file_forms = OrderFileFormSet(self.request.POST or None, self.request.FILES or None, prefix='order_file')
            order_image_forms = OrderImageFormSet(self.request.POST or None, self.request.FILES or None, prefix='order_image')
            
        if self.request.method == 'POST':
            order_text_forms = OrderTextFormSet(self.request.POST, self.request.FILES, prefix='order_text')
            order_file_forms = OrderFileFormSet(self.request.POST, self.request.FILES, prefix='order_file')
            order_image_forms = OrderImageFormSet(self.request.POST, self.request.FILES, prefix='order_image')
        
        return order_text_forms, order_file_forms, order_image_forms
    
    @property
    def default_context(self):
        context = {}
        
        site = site_data()
        site['title'] = 'Share Your Service Requirements Before Proceeding to Payment'
        site['description'] = 'Tailor your service to perfection by sharing your specific requirements with us before you proceed to the payment gateway. Customize every detail to ensure your order aligns perfectly with your needs. Your satisfaction is our priority.'
        
   
        context['price_obj'] = self.price_obj
   
        context['title_and_price'] = title_and_price(self.price_obj, self.request.currency)
        context['price_msg'] = price_msg(self.price_obj)
        
        
        context['service'] = self.service
        context['site_data'] = site
        
        
        
        return context   
    
    def get(self, *args, **kwargs):    
        
        #### get formsets to collect order information
        order_text_forms, order_file_forms, order_image_forms = self.get_formsets()

        currency, amount = converted_amount(self.price_obj, self.request.currency)        
      
        payment_gateways = self.get_valid_payment_gateways(amount)           

        payment_gateways_form = PaymentGatewayForm(payment_gateways=payment_gateways)
        
        context = self.default_context  
        
        context['order_text_forms'] = order_text_forms
        context['order_file_forms'] = order_file_forms
        context['order_image_forms'] = order_image_forms
        context['payment_gateways_form'] = payment_gateways_form
        
        
        ### collect order email
        email_collection_form = EmailCollectionForm(customer_email=self.request.user.email if self.request.user.is_authenticated else None, request=self.request)
      
               
        if not self.request.user.is_authenticated:  
            context['email_collection_form'] = email_collection_form                
        
        
        if settings.SALING_SERVICE:
            return render(self.request, self.template_name, context)
        else:
            raise Http404
    
    def post(self, *args, **kwargs):  
        
        if settings.SALING_SERVICE:
            pass
        else:
            raise Http404
        
        order_text_forms, order_file_forms, order_image_forms = self.get_formsets()
        
        currency, amount = converted_amount(self.price_obj, self.request.currency)        
      
        payment_gateways = self.get_valid_payment_gateways(amount)           

        payment_gateways_form = PaymentGatewayForm(payment_gateways=payment_gateways, data=self.request.POST)
        email_collection_form = EmailCollectionForm(customer_email=None, request=self.request, data = self.request.POST)            
        
        context = self.default_context  
        context['order_text_forms'] = order_text_forms
        context['order_file_forms'] = order_file_forms
        context['order_image_forms'] = order_image_forms
        context['payment_gateways_form'] = payment_gateways_form   
        context['email_collection_form'] = email_collection_form               
        
        
        if not self.request.user.is_authenticated:           
            if email_collection_form.is_valid():      
                customer_email = email_collection_form.cleaned_data['customer_email'] 
                customer = get_or_create_user(customer_email)                
            else: 
                messages.warning(self.request, 'Order email is essential!')
                
                return render(self.request, self.template_name, context)
        else:
            customer = self.request.user
            
            
        order = Order.objects.create(
            price = self.price_obj,   
            currency = currency,
            amount = amount * 1,  
            customer = customer                                  
        ) 
        
        

        
        if order_text_forms.is_valid() and order_file_forms.is_valid() and order_image_forms.is_valid() and payment_gateways_form.is_valid():       
                     
            
            order_texts_to_create = []            
            for form in order_text_forms:            
                try:          
                    data = form.cleaned_data['data']   
                except KeyError:
                    form.add_error('data', "Data is missing or invalid.")               
                    return render(self.request, self.template_name, context)                          
                order_texts_to_create.append(OrderText(order=order, data=data))              
            OrderText.objects.bulk_create(order_texts_to_create)
            
            order_file_to_create = []            
            for form in order_file_forms:              
                file = form.cleaned_data.get('file')         
                order_file_to_create.append(OrderFile(order=order, file=file))                   
            OrderFile.objects.bulk_create(order_file_to_create)
            
            order_image_to_create = []            
            for form in order_image_forms:              
                image = form.cleaned_data.get('image')         
                order_image_to_create.append(OrderImage(order=order, images=image))             
            OrderImage.objects.bulk_create(order_image_to_create)
            
            selected_gateway = payment_gateways_form.cleaned_data['payment_gateway']      
    
            cls = get_payment_method_class(selected_gateway)   
            
            gateway_dict = cls().get_required_dict                
            gateway_dict['order_id'] = order.id          
                
            payment_url = cls().create_payment(**gateway_dict)
 
            return redirect(payment_url)
        else:
            return render(self.request, self.template_name, context)
            


        
    


class CollectRequirements(View):
    http_method_names = ['get', 'post']
    template_name = 'service/collect_requirements.html'      

    
    def get_price(self, pk):
        return get_object_or_404(Price, pk=pk) 
    
    def get_payment_gateways(self):
        # Initialize a dictionary to store payment method URLs
        payment_gateways = {}

        # Process each active payment method
        for payment_method in active_payment_methods:
            if isinstance(payment_method, PaymentGatewayBase): 
                payment_gateways[payment_method.get_gateway_name()] = payment_method.get_help_text()

        
        return payment_gateways
    
    def get_formsets(self, order, request):
        # Create formsets for related models
        OrderTextFormSet = inlineformset_factory(Order,  OrderText, fk_name='order', form = OrderTextForm, extra=1, max_num=12, can_delete=False)
        OrderFileFormSet = inlineformset_factory(Order, OrderFile, fk_name='order', form = OrderFileForm, extra=1, max_num=3, can_delete=False)
        OrderImageFormSet = inlineformset_factory(Order, OrderImage, fk_name='order', form = OrderImageForm, extra=1, max_num=3, can_delete=False)
   
        if request.method == 'GET':
            order_text_forms = OrderTextFormSet(request.POST or None, request.FILES or None, prefix='order_text', instance=order)
            order_file_forms = OrderFileFormSet(request.POST or None, request.FILES or None, prefix='order_file', instance=order)
            order_image_forms = OrderImageFormSet(request.POST or None, request.FILES or None, prefix='order_image', instance=order)
            
        if request.method == 'POST':
            order_text_forms = OrderTextFormSet(request.POST, request.FILES, prefix='order_text', instance=order)
            order_file_forms = OrderFileFormSet(request.POST, request.FILES, prefix='order_file', instance=order)
            order_image_forms = OrderImageFormSet(request.POST, request.FILES, prefix='order_image', instance=order)
        
        return order_text_forms, order_file_forms, order_image_forms
    
    def success_redirect(self, order, service_id):        
        if order.price.is_service:           
            return reverse('service:service_details', args=[service_id])
        elif order.price.is_quotation:
            return reverse('service:web_quotation', args=[service_id])            
        else:
            return reverse('service:service_list')  
        
    def get_mode(self, price):
        
        if price.is_onetime:
            mode = 'payment'  
        elif price.is_subscription:  
            mode = 'subscription'   
        else:
            mode = 'setup'    
            
        return mode
        
    
    def get(self, *args, **kwargs):      
        
        # order_id = kwargs['order_id']   
        # service_id = kwargs['pk1']               
        # order = Order.objects.get(pk=order_id)
          
        # #### no need this page if order successfull     
        # if order.is_allowed_to_checkout:
        #     pass
        # else:
        #     messages.info(request, 'The refering order can not be access, checkout completed succesfully! You can make new order from this page.')  
        #     return redirect(self.success_redirect(order, service_id)) 
            
        
        #### get formsets to collect order information
        order_text_forms, order_file_forms, order_image_forms = self.get_formsets(order, request)

        
        #### get active gateways based on settings.ACTIVE_PAYMENT_METHODS
        payment_gateways = self.get_payment_gateways() 
          
        #### Create the payment URL form to collect selected gateway
        payment_gateways_form = PaymentGatewayForm(payment_gateways=payment_gateways)
        
        context = {     
            'order_text_forms': order_text_forms,
            'order_file_forms': order_file_forms,
            'order_image_forms': order_image_forms,
            'payment_gateways_form': payment_gateways_form,
        }
        
        ### collect order email
        email_collection_form = EmailCollectionForm(customer_email=order.customer.email if order.customer else '')
      
        if not order.customer:            
            if not request.user.is_authenticated:             
                context.update({'email_collection_form' : email_collection_form})
            
        
        site = site_data()
        site['title'] = 'Share Your Service Requirements Before Proceeding to Payment'
        site['description'] = 'Tailor your service to perfection by sharing your specific requirements with us before you proceed to the payment gateway. Customize every detail to ensure your order aligns perfectly with your needs. Your satisfaction is our priority.'
        
        
        context['site_data'] = site

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):     
        
        order_id = kwargs['order_id']    
        service_id = kwargs['pk1']  
        price_id = kwargs['pk2']                
                      
        order = Order.objects.get(pk=order_id)      
        
        #### no need this page if order successfull     
        if order.is_allowed_to_checkout:
            pass
        else:
            messages.info(request, 'The refering order can not be access, checkout completed succesfully! You can make new order from this page.')  
            return redirect(self.success_redirect(order, service_id))     

        
        #### get formsets to collect order information
        order_text_forms, order_file_forms, order_image_forms = self.get_formsets(order, request)   

        #### get active gateways based on settings.ACTIVE_PAYMENT_METHODS
        payment_gateways = self.get_payment_gateways()   
        #### Create the payment URL form to collect selected gateway       
        payment_gateways_form = PaymentGatewayForm(payment_gateways=payment_gateways, data=request.POST)    
        
        ### get or make customer. it is essential to followup abandoned order as we can decide customer form here
        if not order.customer:
            if not request.user.is_authenticated:
                ### collect order email
                email_collection_form = EmailCollectionForm(customer_email=order.customer.email if order.customer else '', data = request.POST)
                
                if email_collection_form.is_valid():
                    ### NEED TO CHECK POSTING EMAIL AND ORDER EMAIL ARE SAME
                    customer_email = email_collection_form.cleaned_data['customer_email'] 
                    customer = get_or_create_user(customer_email)
                    
                else:               
                    messages.warning(request, 'Order email is essential!')
                    return redirect(request.path)  
            else:
                customer = request.user
                email_collection_form = None
        else:
            customer = order.customer
            email_collection_form = None
                 
    

        if order_text_forms.is_valid() and order_file_forms.is_valid() and order_image_forms.is_valid() and payment_gateways_form.is_valid():       
            
            order_text_forms.save()
            order_file_forms.save()
            order_image_forms.save()      
            
            #### data for order from pre-built service to sent to gateway   
            if order.price.is_service:  
                service = order.price.service
                price = order.price
                
                product_name = service.name
                product_description = service.description
                
                interval = price.interval
                interval_count = price.interval_count
                
                symbol, amount = converted_amount(price, request.currency)
                
                mode = self.get_mode(price)
                
   
                
            
            #### data for order from quotatiom to sent to gateway        
            if order.price.is_quotation:
                quotation = order.price.quotation
                price = order.price 
                
                product_name = quotation.name
                product_description = quotation.explanations
                
                interval = price.interval
                interval_count = price.interval_count
                
                #### get converted amount based on user selected currency
                symbol, amount = converted_amount(price, request.currency)
                
                #### decide perfect mode for stripe gateway
                mode = self.get_mode(price)
               
                
          
               
             
            if 'payment_gateway' in payment_gateways_form.cleaned_data and payment_gateways_form.cleaned_data['payment_gateway'] is not None:       
                #### find gateway class based on user selction gateway name and gateway moudule name are same.
                selected_gateway = payment_gateways_form.cleaned_data['payment_gateway']  
            else:
                log.warning('No payment gateway found to proced!')
                messages.warning(request, 'No payment gateway found to proced!')
                return redirect(request.path)  
            
                    
            cls = get_payment_method_class(selected_gateway)   
            
            #### build gateway dict
            gateway_dict = {
                'success_url' : f"{request.build_absolute_uri(reverse('shop:payment_success'))}" + "?session_id={CHECKOUT_SESSION_ID}" + f"&selected_gateway={selected_gateway}",
                'cancel_url' : f"{request.build_absolute_uri(reverse('shop:payment_cancel'))}" + "?session_id={CHECKOUT_SESSION_ID}" + f"&selected_gateway={selected_gateway}",
                'client_reference_id' : str(order_id),
                'currency' : (request.currency).lower(),
                'mode' : mode,
                'after_expiration__recovery__enabled' : True,
                'after_expiration__recovery__allow_promotion_codes' : True,
                'automatic_tax__enabled' : True,                
                'locale' : 'auto',
                'phone_number_collection__enabled' : True,              
                'tax_id_collection__enabled' : True,                
                'line_items__price_data__currency' : (request.currency).lower(),
                'line_items__price_data__unit_amount_decimal' : int(amount * 100),
                'line_items__price_data__tax_behavior': 'exclusive',
                
                'line_items__price_data__product_data__name' : product_name,
                'line_items__price_data__product_data__description' : product_description,
                'line_items__price_data__product_data__tax_code' : 'txcd_10000000', # for stripe
                
                'line_items__price_data__recurring__interval' : interval,
                'line_items__price_data__recurring__interval_count' : interval_count,
                'line_items__quantity': 1,
            
            }  
            
            
            
            ### to ensure no duplicate customer in stripe gateway
            if customer.gateway_customer_reference:
                gateway_dict.update(
                    {
                    'customer' : customer.gateway_customer_reference
                    }
                )
            else:
                gateway_dict.update(
                    {
                        'customer_email' : customer.email
                    }
                )
              
            ## assign customer to order  
            order.customer = customer
            order.save()
                
            
            payment_url = cls().create_payment(**gateway_dict)
            
            
            #### redirect
            if payment_url is not None: 
                log.info(f'payment url found. redirecting to {selected_gateway} checkout for order {order.id}!')                
                #### redirect to gateway's payment processing
                return redirect(payment_url, code=303)
            else:
                log.warning(f'ALERT! PAYMENT URL NOT FOUND! REDIRECTING TO {request.path} !!!!!!!!!!!!')  
                messages.warning(request, 'There was problem in forwarding payment gateway! We are sorry for inconvenience! Please come back later! We are working on the issues!')
                return HttpResponseRedirect(request.path)
        else:
            pass
            
       
        context = {
            'order_text_forms': order_text_forms,
            'order_file_forms': order_file_forms,
            'order_image_forms': order_image_forms,
            'payment_gateways_form': payment_gateways_form,
        } 
        
        
        
        if email_collection_form:
            context.update({'email_collection_form' : email_collection_form})   
        
        site = site_data()
        site['title'] = 'Share Your Service Requirements Before Proceeding to Payment'
        site['description'] = 'Tailor your service to perfection by sharing your specific requirements with us before you proceed to the payment gateway. Customize every detail to ensure your order aligns perfectly with your needs. Your satisfaction is our priority.'
        
        
        context['site_data'] = site   

        return render(request, self.template_name, context)
    
def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def get_or_create_user(email):
    try:    
        user = User.objects.get(email=email)                
    except Exception as e:        
        random_password = generate_random_password()
        user = User.objects.create(email=email)
        user.set_password(random_password)
        user.save()
        
        # Send an email to the user
        subject = f'{site_data()["name"]} - Your New Account Information'
        message =   f'Hello {user.username},\n\n'
        message +=  f'Your account has been created successfully with an order successfully placed on sincehence.co.uk. \n\n' 
        message +=  f'Your initial password is: {random_password}. \n\n' 
        message +=  f'Please change this password! Alternatively you may keep record of this password.\n\n'                     
        message +=  f'Please login to your account and change your password immediately for security reasons.\n\n' 
        message +=  f'Best Regards...\n\n' 
        message +=  f'{site_data()["name"]} TEAM\n\n'

        from_email = settings.DEFAULT_FROM_EMAIL     
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list)
        
        return user

    
def payment_success(request):    
   
    checkout_session_id = request.GET.get('session_id', None)
    selected_gateway = request.GET.get('selected_gateway', None)
    
    cls = get_payment_method_class(selected_gateway)   
    session_data = cls().get_session_response(checkout_session_id)    

    ### get or create user and login
    customer_email = session_data.get('customer_email')   
    user = get_or_create_user(customer_email)   
    
    gateway_customer_reference = session_data.get('customer_id_gateway')  
    if not user.gateway_customer_reference:
        if gateway_customer_reference is not None:
            user.gateway_customer_reference = gateway_customer_reference
            user.save()       
    
    ### update order    
    order_id = uuid.UUID(session_data.get('order_id'))
    order = Order.objects.get(pk = order_id)  
    if not order.customer:  
        order.customer = user   
    order.gateway = selected_gateway
    order.gateway_reference = checkout_session_id    
    order.status = 'processing'          
    order.save()    
    
    if order.price.is_service:
        item_title = order.price.service.name
        trans_for = 'service'
        remarks = 'service selling'
        
    if order.price.is_quotation:
        item_title = order.price.quotation.name
        trans_for = 'quotation'
        remarks = 'selling from quotation'
        
    price_title = order.price.name
    trans_type = 'add'
    
        
    
    
    ## create subsription    
    
    mode = session_data.get('mode')
    if mode == 'subscription':   
     
        order.gateway_reference2 = session_data.get('subscription_id')     
        
        start_date = datetime.fromtimestamp(int(session_data.get('created_date')), tz=timezone.get_current_timezone())
        end_date = datetime.fromtimestamp(int(session_data.get('expires_at')), tz=timezone.get_current_timezone())

        # Assuming 'order' is a model instance
        order.start_date = start_date
        order.end_date = end_date
        order.subscription_active = True
        order.save()  
        
    if mode == 'payment':
        startdate = timezone.now()
        interval = order.price.interval
        delivery_data = calculate_delivery_date(startdate, interval)
        order.start_date = startdate
        order.tentative_delivery = delivery_data
        order.save()
        
   
        
    ### create transection  
    trans_para = {
        'order' : order,
        'payment_status' : 'authorized',
        'payment_gateway' : selected_gateway,
        'gateway_reference' :  session_data.get('payment_intent'),
        'gateway_invoice' : session_data.get('invoice_id'),   
        'amount_subtotal' : int(session_data.get('amount_subtotal'))/100,   
        'amount_total' : int(session_data.get('amount_total'))/100,  
        'paymemt_currency' :  Currency.objects.get(code = (session_data.get('order_currency')).upper()),
        'autoamtic_tax' : session_data.get('automatic_tax_status'),
        'customer': order.customer ,
        'item_title' : item_title,
        'price_title' : price_title,
        'trans_type' : trans_type,
        'trans_for' : trans_for,
        'remarks' : remarks      
        
        
    }    
    
    transaction = Transaction.objects.create(**trans_para)    
    transaction.save() 

    
    # Send an email to the user
    subject = 'SINCEHENCE LTD - Order has been placed!'
    message = f'Hello {user.username},\n\n' \
            f'This message serves as confirmation that you have successfully placed an order with reference to Order ID {order.id}. \n\n' \
            f'Your payment has been authorized!\n\n' \
            f'You will receive an email notification once the payment has been processed by us.\n\n' \
            f'Best Regards...\n\n' \
            f'SINCEHENCE TEAM\n\n'

    from_email = settings.DEFAULT_FROM_EMAIL     
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)

    context = {
        'order': order,            
    }    
    
    site = site_data()
    site['title'] = 'Order Placed successfully!'
    site['description'] = 'This is a order confirmation notification.'    
    
    context['site_data'] = site   

    return render(request, 'shop/success.html', context)
    

def payment_cancel(request):
    checkout_session_id = request.GET.get('session_id', None)
    selected_gateway = request.GET.get('selected_gateway', None)     
    
    cls = get_payment_method_class(selected_gateway)   
    session_data = cls().get_session_response(checkout_session_id)    
    order_id = uuid.UUID(session_data.get('order_id'))
    order = Order.objects.get(pk = order_id)   
    order.status = 'abandoned'
    order.gateway_payment_url = session_data.get('url')
    order.save()   
    
    context = {
        'order': order,            
    }  
    
    site = site_data()
    site['title'] = 'Order Cancelled!'
    site['description'] = 'No issue has been happend. You may continue from this page!'
    context['site_data'] = site   

    return render(request, 'shop/cancel.html', context)


class QuotationRequest(LoginRequiredMixin, View):
    http_method_names = ['get', 'post']
    template_name = 'shop/quotation_request.html'  
    
    def get_service(self, pk):
        data = Service.objects.prefetch_related('service_meta_data', 'service_features').get(pk=pk) 
        return data
    
    def get(self, request, *args, **kwargs):  
        reference_service = self.get_service(kwargs['pk']) 
        
        form = QuotationForm(initial={'creator': request.user, 'reference_service': reference_service})
        
        formatted_prices = get_formatted_prices(reference_service, request.currency)
        reference_service_form = ServicePriceForm(prices=reference_service.prices_of_service.all(), formatted_prices=formatted_prices)
        
        context ={
            'form' : form,
            'reference_service_form' : reference_service_form,
            'reference_service' : reference_service
        }
        site = site_data()
        site['title'] = 'Requesting Tailored Services to Meet Your Unique Needs'
        site['description'] = 'Use our intuitive form to articulate your specific requirements to create custom solutions that align perfectly with your goals or consider choosing an existing plan'
        
        
        context['site_data'] = site

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):    
        
        reference_service = self.get_service(kwargs['pk']) 
        
        form = QuotationForm(request.POST, initial={'creator': request.user, 'reference_service': reference_service})
        
        formatted_prices = get_formatted_prices(reference_service, request.currency)

        reference_service_form = ServicePriceForm(prices=reference_service.prices_of_service.all(), formatted_prices=formatted_prices, data=request.POST)
        
           
        if form.is_valid():
            # Save the form data to create a new QuotationRequest instance
            quotation_request = form.save(commit=False)
            quotation_request.creator = request.user
            quotation_request.reference_service = reference_service
            quotation_request.save()
            messages.success(request, f'Quotation request {quotation_request.pk} has been submitted! We will review it and get back to you soon!')
            return redirect(request.path)
        
        context ={
            'form' : form,
            'reference_service_form' : reference_service_form,
            'reference_service' : reference_service
        } 
        
        site = site_data()
        site['title'] = 'Requesting Tailored Services to Meet Your Unique Needs'
        site['description'] = 'Use our intuitive form to articulate your specific requirements to create custom solutions that align perfectly with your goals or consider choosing an existing plan'
        
        
        context['site_data'] = site

        return render(request, self.template_name, context)  
    
    
@method_decorator(login_required, name='dispatch')
@method_decorator(quotation_creator_required, name='dispatch')
class QuotationDetail(View):
    http_method_names = ['get', 'post']
    template_name = 'shop/quotation_web.html' 
    
    
    def get_obj(self, pk):
        data = get_object_or_404(Quotation, pk=pk)
        return data
    
  
    
    def is_valid_id(self, submited_id, pk):
        if uuid.UUID(submited_id) == self.get_obj(pk).pk:
            return True
        return False        
    
    def get(self, request, *args, **kwargs):   
          
        pk1 = kwargs['pk']
        quotation = self.get_obj(pk1)   
        
        form = AcceptForm(initial={'hidden_field': pk1})
        reject_form = RejectForm(initial={'reject_field' : pk1})
             
        context ={    
            'quotation' : quotation,
            'form' : form,
            'reject_form' : reject_form,
            
        }
        context['site_name'] = site_data()
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
                
        pk1 = kwargs['pk']
        quotation = self.get_obj(pk1)   
      
        form = AcceptForm(initial={'hidden_field': pk1}, data=request.POST)      
        reject_form = RejectForm(initial={'reject_field': pk1}, data=request.POST)       
        

        if form.is_valid():           
            quotation_id = form.cleaned_data['hidden_field']              
            
            if not self.is_valid_id(quotation_id, pk1):
                raise Http404("Quotation not found")
            
            quotation.status = 'accepted_by_client'
            quotation.save()            
                   
            pk2 = quotation.prices_of_quotation.pk    
            price = quotation.prices_of_quotation
            order = Order.objects.create(
                price = price
               
            )   
            if order.price.is_quotation:
                quotation_todos = quotation.quotation_todo.all()     
                if quotation_todos.exists():
                    ordertext_to_add = []
                    for todo in quotation_todos:
                        ordertext_to_add.append(OrderText(order=order, data=todo.data)) 
                    OrderText.objects.bulk_create(ordertext_to_add)
            return HttpResponseRedirect(reverse('shop:collect_requirements', args=[order.id, pk1, pk2]))
        
        if reject_form.is_valid():
            quotation_id = reject_form.cleaned_data['reject_field']      
                    
            if not self.is_valid_id(quotation_id, pk1):
                raise Http404("Quotation not found")
                       
            quotation.status = 'rejected_by_client'
            quotation.save()
            
            return  redirect(request.path) 
            

        context = {
            'quotation': quotation,
            'form': form,
            'reject_form' : reject_form,
        }

        return render(request, self.template_name, context)
    
from reportlab.lib.pagesizes import A4     
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas    

@method_decorator(login_required, name='dispatch')
@method_decorator(quotation_creator_required, name='dispatch')
class QuotationPDF(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
        self.ps = A4
        self.pw = A4[0]
        self.ph = A4[1]
        
        self.leftMargin = 0.5 * inch
        self.rightMargin = 0.5 * inch
        self.topMargin = 0.5 * inch
        self.bottomMargin = 0.5 * inch
        
        self._header_height = 0
        self._footer_height = 0
        
        self.pk = None
        self.quotation = None
        
        
    def header_footer(self, canvas, doc):    
        
        #### initializing canvas
        canvas.saveState()    
        
        #### Initializing header table data
        header_table_data = [
            ['QUOTE', f"{remove_dash_hyphen_capital(self.quotation.status)}", f"Valid till {self.quotation.quotation_data.valid_till.strftime('%Y-%m-%d')}"],                      
            [f'{self.quotation.quotation_data.header.upper()}', '', f'{convert_amount(self.quotation.prices_of_quotation, self.request.currency)}']
        ]
        header_table = Table(header_table_data, colWidths=[self.pw/3 - self.leftMargin, self.pw/3, self.pw/3 - self.rightMargin])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),            
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, 1), 15),  # Set the font size to 12 for the second row
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.grey),  # Set text color to black for the second row         
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.black),  # Set text color to black for the second row
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),  # Make the second row bold
           
        ])) 
        #### Writing Header Table on canvas
        header_table.wrapOn(canvas, self.pw, self.topMargin)
        header_table.drawOn(canvas, self.leftMargin, self.ph - header_table._height-self.topMargin)  
        
        #### updating header heignt
        self._header_height = header_table._height      
        
        # Draw a line under the header table
        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(0.5)
        canvas.line(self.leftMargin, self.ph - header_table._height-self.topMargin - 0.3 * inch , self.pw - self.leftMargin, self.ph - header_table._height-self.topMargin - 0.3 * inch )    
        
        #### saving canvas
        canvas.restoreState()

        #### Initializing canvas to write footer       
        canvas.saveState()  
        #### retrinving page number
        page_number = canvas.getPageNumber()  
        
        #### Initializing footer table data     
        footer_table_data = [[f'{self.quotation.quotation_data.footer}', f'{self.quotation.quotation_data.quotation_number.upper()}__PAGE-{page_number}']]
        footer_table = Table(footer_table_data, colWidths=[self.pw/2 - self.leftMargin, self.pw/2 - self.rightMargin])
        footer_table.setStyle(TableStyle([                
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.grey),  # Set text color to black for the second row       
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
            ]))
        #### Writing Footer Table on canvas
        footer_table.wrapOn(canvas, self.pw, self.bottomMargin)
        footer_table.drawOn(canvas, self.leftMargin, footer_table._height )  # Adjust the position as needed
        #### updating footer heignt
        self._footer_height = footer_table._height     
        
        #### Draw a line before the footer table
        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(0.5)
        canvas.line(self.leftMargin, self.bottomMargin + footer_table._height, self.pw - self.rightMargin, self.bottomMargin + footer_table._height)     
        
        #### Saving canvas   
        canvas.restoreState()
        
    
    def get(self, request, *args, **kwargs):
                 
        pk = kwargs['pk']
        
        #### updating PK
        self.pk = pk
        quotation = get_object_or_404(Quotation, pk=pk)
        
        #### Updating quotation to access in the header
        self.quotation = quotation 
        
        site = site_data()   
        
        buffer = io.BytesIO() 
      
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=self.ps, 
            leftMargin=self.leftMargin, 
            rightMargin=self.rightMargin, 
            topMargin=self.topMargin, 
            bottomMargin=self.bottomMargin
            )    
        
        ### running to get header and footer heigt
        self.header_footer(canvas.Canvas(buffer), doc)        
        
        ### redefining workable area
        doc.topMargin = self._header_height + self.topMargin
        doc.bottomMargin = self._footer_height + self.bottomMargin  
        
        title = f'Quotation__#{quotation.quotation_data.quotation_number}_SinceHence'    
        doc.title = title
        doc.author = f'{site["name"]}'  
        doc.creator = f'{site["name"]}'  
        doc.producer = f'{site["name"]}'
        
        styles = getSampleStyleSheet()           

        left_style = ParagraphStyle(name='LeftStyle', alignment=0, fontName="Helvetica")
        left_style2 = ParagraphStyle(name='LeftStyle2', alignment=0, fontName="Helvetica", textColor=colors.gray)
        
        ### defining quotation data list
        Story = []
        
        #### quotation sender name and email at left
        Story.append(Spacer(0.5 * inch, 0.5 * inch))  
        site_name =  site['name'].upper()
        site_email =  site['email']        
        Story.append(Paragraph(f'{site_name}', left_style))
        Story.append(Paragraph(f'{site_email}', left_style2))
        
        
        
        #### quotation summary at right
        qi_data = [
            ['', '', f'QUOTE NUMBER', f"{quotation.quotation_data.quotation_number}"],
            ['', '', f'ISSUE DATE', f"{quotation.quotation_data.created_at.strftime('%Y-%m-%d')}"],
            ['', '', f'EXPIRATION DATE', f"{quotation.quotation_data.valid_till.strftime('%Y-%m-%d')}"]    
        ]
        
        qi_table = Table(qi_data, colWidths=[self.pw/4 - self.leftMargin, self.pw/4, self.pw/4, self.pw/4 - self.rightMargin])
        qi_table.setStyle(TableStyle([
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),  # Align the 'QUOTE' column to the right
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),  # Align the fourth column to the right
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12), 
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.gray),  # Set text color to black for the 'QUOTE' column
        ]))        
        Story.append(qi_table)
        
         
        #### Quotation for and memo       
        cell_style = ParagraphStyle(name='cell_style', alignment=0, fontName="Helvetica-Bold", textColor = colors.gray, fontSize = 10)
        cell_style2 = ParagraphStyle(name='cell_style2', alignment=4, fontName="Helvetica", textColor = colors.gray, fontSize = 8)        
        tom_data = [
            [f'QUOTE FOR', ''],
            [Paragraph(f'{get_user_identity(quotation.creator)}', cell_style), Paragraph(f'{quotation.quotation_data.memo }', cell_style2 )]        
        ]   
        tom_table = Table(tom_data, colWidths=[self.pw/3 - self.leftMargin, self.pw/3 * 2 - self.rightMargin], splitByRow=1)
        tom_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),   
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),           
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.gray), 
            
        ]))        
        Story.append(tom_table)
        Story.append(Spacer(0.5 * inch, 0.25 * inch))
        
        
        #### Product and price information
        qt_data = [
            ['SERVICE AND DESCRIPTION', "PRICE DETAILS"],            
            [Paragraph(f'<b>{quotation.name.upper()}</b><br />{quotation.explanations}', cell_style), Paragraph(f'{formatedprice(quotation.prices_of_quotation, request.currency, Story) }', cell_style2)]
            
            ]
        qt_table = Table(qt_data, colWidths=[self.pw/2 - 0.5 * inch, self.pw/2 - 0.5 * inch])
        qt_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),          
            ('LINEBELOW', (0, 0), (-1, 0), 1, (0, 0, 0)),  # Line below the first row
            ('LINEBELOW', (0, -1), (-1, -1), 1, (0, 0, 0)),  # Line below the last ro
        ]))
        Story.append(qt_table)
        Story.append(Spacer(0.5 * inch, 0.25 * inch))
        
        #### building PDF with header and footer
        doc.build(Story, onFirstPage=self.header_footer, onLaterPages=self.header_footer)
        buffer.seek(0)

        # Return the PDF as a Django response
        response = FileResponse(buffer, as_attachment=False, filename=f"{title}.pdf")
        return response





def update_payment(request, id):
    template = 'service/update_payment.html'
    order = get_object_or_404(Order, id=id)
    
    if order.customer == request.user:
        pass
    else:
        raise Http404
    
    invoice = order.invoice
     
    if int(order.trans_amount) >= int(order.amount):
        invoice.due = False
        invoice.save()
        messages.warning(request, 'It appears that the payment for your order has been successfully processed. If you believe this is in error or have any concerns, please do not hesitate to contact our sales team at sales@sankarmath.org. Your honesty and feedback are greatly appreciated, and we are here to assist you promptly.')
        return 
    
    context = {}
    latest_activities, all_activities = user_activities(request)
    context['latest_activities'] = latest_activities
    context['all_activities'] = all_activities    
    
    next = request.GET.get('next')
    if next:
        redirect_to = next
    else:
        redirect_to = reverse('accounts:user_dashboard')
    
    
    payment_form = PaymentForm(currency = order.currency)   
     
    if request.method == 'POST':  
        payment_form = PaymentForm(data=request.POST, files=request.FILES, currency = order.currency)
        if payment_form.is_valid():            
            print(payment_form.currency)
      
            transaction = payment_form.save(commit=False)            
            transaction.order = order
            transaction.gateway = invoice.gateway 
            transaction.paymemt_currency = payment_form.currency     
            transaction.customer = request.user     
            transaction.save(request=request) # transaction need request
            
            order.status = settings.PAYMENT_PROCESSING_STATUS
            order.save()
            
            if order.pending_amount <= 0:
                invoice.due = False
            invoice.paid_on = timezone.now()
            invoice.save()   
             
            messages.success(request, 'Invoice Payment Updated!') 
            
            return HttpResponseRedirect(redirect_to)
        else:        
            context['payment_form'] =  payment_form    
            context['order'] =  order   
            return render(request, template, context)
        
    context['payment_form'] =  payment_form    
    context['order'] =  order      
    return render(request, template, context)

def cancel_order(request, id):
    order = get_object_or_404(Order, id=id)
    
    next = request.GET.get('next')
    if next:
        redirect_to = next
    else:
        redirect_to = reverse('accounts:user_dashboard')
    
    if order.customer == request.user:
        pass
    else:
        messages.warning(request, 'It is not your order, operation cannot done.')
        return redirect(redirect_to)
    
    if order.status in settings.PAYMENT_PENDING_STATUS and not order.has_transactions:
        order.status = 'abandoned'
        order.save()
        messages.warning(request, f'{order.order_number} is in trash! you can not resume this order anymore.')
    else:
        messages.warning(request, 'The operation can not be done as it has transactions.')
        
    return redirect(redirect_to)
    

    

  


