
from django import forms
from django.contrib import admin
import json
from core.templatetags.core import formatedprice
from .models import *
        
       

class PriceAdminForm(forms.ModelForm):
    class Meta:
        model = Price
        fields = '__all__'
        
class OrderTextForm(forms.Form):
    data = forms.CharField(widget=forms.TextInput(), required=True)  
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        # Add Bootstrap classes to the widget
        self.fields['data'].widget.attrs.update({'class': 'form-control form-control-lg'})
        
        # Add a label
        self.fields['data'].label = 'To-do line'
        


class OrderFileForm(forms.Form):
    file = forms.FileField()
    # class Meta:
    #     model = OrderFile
    #     fields = ['id','file']
        
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to the widget
        self.fields['file'].widget.attrs.update({'class': 'form-control form-control-lg'})
        
        # Add a label
        self.fields['file'].label = 'Upload PDF document'
        
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Define the allowed extensions and max file size
            allowed_extensions = ['pdf']
            max_file_size = 5 * 1024 * 1024  # 1 MB limit

            # Validate file extension
            extension_validator = FileExtensionValidator(
                allowed_extensions=allowed_extensions,
                message='Only PDF files are allowed.'
            )
            extension_validator(file)

            # Validate file size
            size_validator = MaxLengthValidator(
                limit_value=max_file_size,
                message='File size must be less than 5 MB.'
            )
            size_validator(file)

        return file

class OrderImageForm(forms.Form):
    image = forms.ImageField()
    # class Meta:
    #     model = OrderImage
    #     fields = ['id','images']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to the widget
        self.fields['image'].widget.attrs.update({'class': 'form-control form-control-lg'})
        
        # Add a label
        self.fields['image'].label = 'Project Images'
        
    def clean_images(self):
        images = self.cleaned_data.get('image')
        if images:
            # Define the allowed extensions and max file size
            allowed_extensions = ['png', 'jpg', 'jpeg']
            max_file_size = 1 * 1024 * 1024  # 1 MB limit

            # Validate file extension
            extension_validator = FileExtensionValidator(
                allowed_extensions=allowed_extensions,
                message='Only PNG, JPG, JPEG files are allowed.'
            )
            extension_validator(images)

            # Validate file size
            size_validator = MaxLengthValidator(
                limit_value=max_file_size,
                message='File size must be less than 1 MB.'
            )
            size_validator(images)

        return images
        
# def validate_payment_url(value):
#     # Add your custom validation logic here
#     # For example, check if the selected payment URL is valid
#     # if not is_valid_payment_url(value):
#     #     raise ValidationError('Invalid payment URL')
#     print(value)
#     print('checked_____________')
    
# class CustomChoiceField(forms.ChoiceField):
#     def validate(self, value):
#         # Skip the default validation for ChoiceField
#         pass

class PaymentGatewayForm(forms.Form):
    payment_gateway = forms.ChoiceField(
        choices=[], 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}), 
        required=True, 
        error_messages={'required': 'Please select a Payment Gateway'},
 
    )

    def __init__(self, payment_gateways, *args, **kwargs):
        super(PaymentGatewayForm, self).__init__(*args, **kwargs)
        self.fields['payment_gateway'].choices = [(key, value) for key, value in payment_gateways.items()]    
        

        
class EmailCollectionForm(forms.Form):
    customer_email = forms.EmailField(
        label='Email Address', 
        max_length=100, 
        error_messages={'required':'Customer Email Required!'}, 
        help_text="By providing your email, system will create an account, If no account is currently associated with this email, a new account will be established, and any payments will be linked to this email and account. Upon successful account creation, we will send you your account details, including a password. You have the option to customize your password to something memorable, or you can choose to keep the system-generated one."
        )  
    
    def __init__(self, customer_email, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(EmailCollectionForm, self).__init__(*args, **kwargs)
        self.fields['customer_email'].label = ''
        self.fields['customer_email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter Email address'})
        
        if customer_email:
            self.fields['customer_email'].initial = customer_email
            
    def clean_customer_email(self):        
        customer_email = self.cleaned_data.get('customer_email')
        if customer_email is not None: 
            if self.request.user.is_authenticated:     
                if customer_email != self.request.user.email:            
                    raise forms.ValidationError('Default user email cannot be changed! If you wise order using deiffernet email then please logout!')
                
        return customer_email
        

        
       

    
    
class ServicePriceForm(forms.Form):
    price_id = forms.ChoiceField(choices=[], widget=forms.RadioSelect(attrs={'class': 'form-check-input'}), required=True, error_messages={'required': 'Please select a price option to proced'})

    def __init__(self, prices, formatted_prices, *args, **kwargs):
        super(ServicePriceForm, self).__init__(*args, **kwargs)
        self.fields['price_id'].choices = [(price.id, formatted_price) for price, formatted_price in zip(prices, formatted_prices)]
        
class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ['name', 'explanations', 'require_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        
        self.fields['require_by'].widget = forms.TextInput(attrs={'class': 'form-control datepicker', 'placeholder':'e.g. YYYY-MM-DD'})

        # self.fields['nice_title'].label = 'Custom Nice Title Label'
        # self.fields['explanations'].label = 'Custom Explanations Label'
        # self.fields['require_by'].label = 'Date you can wait to get quotation'
        
        
class AcceptForm(forms.Form):
    hidden_field = forms.CharField(widget=forms.HiddenInput())
    
class RejectForm(forms.Form):
    reject_field = forms.CharField(widget=forms.HiddenInput())
    
    
class PaymentForm(forms.ModelForm):
    
    def __init__(self, currency, *args, **kwargs):        
        self.currency = currency        
        super().__init__(*args, **kwargs)   
        self.fields['amount'].label = f'Paid Amount in {self.currency}'
        
    class Meta:
        model = OrderTransaction
        fields = ['amount', 'trxID', 'mobile', 'screenshoot']
        
        widgets = {
            'amount' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Paid Amount'}),
            'trxID' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Transacion ID you receive', 'row': 5}),
            'mobile' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter  mobile number that amount paid from'}),
            'screenshoot' : forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'Enter screenshoot'}),
            
            
        }
        labels = {
            # 'amount' : f'Paid Amount',
            'trxID' : 'TrxID',
            'mobile' : 'Mobile Number',
            'screenshoot' : 'Add Photo or PDF for transaction receipt!'
            
        }
        