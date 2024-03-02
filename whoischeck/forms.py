from django import forms
from .models import WhoisResult
from captcha.widgets import ReCaptchaV2Invisible, ReCaptchaV2Checkbox
from captcha.fields import ReCaptchaField
import validators

class DomainForm(forms.ModelForm):
    captcha = ReCaptchaField( widget=ReCaptchaV2Checkbox)  
    
    def clean_domain_name(self):
        domain_name = self.cleaned_data['domain_name']

        is_valid = validators.domain(domain_name)
        
        if is_valid:
            return domain_name        
        else:
            raise forms.ValidationError('Enter Valid Domain name!')
        

    
    
    class Meta:
        model = WhoisResult
        fields = ['domain_name']
        
        widgets = {                      
            'domain_name': forms.TextInput(attrs={'class':'form-control form-control-lg','placeholder': 'Enter domain e.g.: example.com', 'aria-label':'domain_name',  }),             
        } 