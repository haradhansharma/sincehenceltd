from django import forms
from .models import DiscussionRecord, OrderShippingRecord, ProformaInvoice, SourcingOrder, SourcingProgress, SupplierProfile, ProductLink
from accounts.forms import DateInput
class SupplierForm(forms.ModelForm):
    class Meta:
        model = SupplierProfile
        fields = ['name', 'company', 'contact_information', 'website', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_information': forms.Textarea(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control'}),
        }
class ProductLinkForm(forms.ModelForm):
    class Meta:
        model = ProductLink
        fields = ['link_title', 'product_type', 'url','link_img_url', 'importance', 'notes']
        widgets = {
            'link_title': forms.TextInput(attrs={'class': 'form-control'}), 
            'product_type': forms.TextInput(attrs={'class': 'form-control'}),          
                       
            'importance': forms.Select(attrs={'class': 'form-select'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'link_img_url': forms.URLInput(attrs={'class': 'form-control'}),            
            'notes': forms.Textarea(attrs={'class': 'form-control'}),
        }
        
class DiscussionRecordForm(forms.ModelForm):
    class Meta:
        model = DiscussionRecord
        fields = ['date', 'discussion_details']
        
        widgets = {                      
            'discussion_details': forms.Textarea(attrs={'placeholder': 'discussion_details', 'class':'form-control', 'aria-label':'discussion_details' }),   
            'date': DateInput(attrs={'data-datepicker': "" , 'class':'form-control', 'aria-label':'date', }),            
            
        }
        
        
class SourcingProgressForm(forms.ModelForm):
    class Meta:
        model = SourcingProgress
        fields = ['progress_status', 'progress_notes']
        
        widgets = {
            'progress_status': forms.Select(attrs={'class': 'form-select'}),
            'progress_notes': forms.Textarea(attrs={'class': 'form-control'}),
        }
        
        
class ProformaInvoiceForm(forms.ModelForm):
    class Meta:
        model = ProformaInvoice
        fields = ['invoice_number', 'date', 'amount', 'attachments']
        
        widgets = {                      
            'invoice_number': forms.TextInput(attrs={'placeholder': 'invoice_number', 'class':'form-control', 'aria-label':'invoice_number' }), 
            'attachments': forms.FileInput(attrs={'placeholder': 'attachments', 'class':'form-control', 'aria-label':'attachments' }),               
            'amount': forms.TextInput(attrs={'placeholder': 'amount', 'class':'form-control', 'aria-label':'amount' }),  
            'date': DateInput(attrs={'data-datepicker': "" , 'class':'form-control', 'aria-label':'date', }),            
            
        }
        
class SourcingOrderForm(forms.ModelForm):
    class Meta:
        model = SourcingOrder
        fields = ['order_number', 'date', 'quantity', 'price']
        
        widgets = {                      
            'order_number': forms.TextInput(attrs={'placeholder': 'order_number', 'class':'form-control', 'aria-label':'order_number' }), 
            'quantity': forms.TextInput(attrs={'placeholder': 'quantity', 'class':'form-control', 'aria-label':'quantity' }), 
            'price': forms.TextInput(attrs={'placeholder': 'price', 'class':'form-control', 'aria-label':'price' }),    
            'date': DateInput(attrs={'data-datepicker': "" , 'class':'form-control', 'aria-label':'date', }),            
            
        }
        
class OrderShippingRecordForm(forms.ModelForm):
    class Meta:
        model = OrderShippingRecord
        fields = ['shipping_date', 'shipping_details']
        
        widgets = {
            'shipping_date': DateInput(attrs={'data-datepicker': "" , 'class':'form-control', 'aria-label':'shipping_date', }),     
            'shipping_details': forms.Textarea(attrs={'class': 'form-control'}),
        }
        