from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, 
    UserChangeForm, 
    AuthenticationForm, 
    PasswordResetForm, 
    SetPasswordForm, 
    PasswordChangeForm
)
from django_countries import countries

from service.models import Interactions 
from .models import *
from .tokens import account_activation_token
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.contrib.auth import authenticate
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible, ReCaptchaV2Checkbox
from phonenumber_field.widgets import PhoneNumberPrefixWidget, RegionalPhoneNumberWidget, PhonePrefixSelect

class AvatarForm(forms.ModelForm):
    class Meta:       
        
        model = Profile
        fields = ('avatar',)
        
        widgets = {  
            'avatar': forms.FileInput(attrs={ 'class':'form-control', 'aria-label':'Avatar' }),   
        }
        

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name', 'email', 'organization', 'phone', ) 
        
        widgets = {                      
            'username': forms.TextInput(attrs={'placeholder': 'username', 'class':'form-control', 'aria-label':'username',  }),
            'first_name': forms.TextInput(attrs={'placeholder': 'first_name', 'class':'form-control', 'aria-label':'first_name' }),
            'last_name': forms.TextInput(attrs={'placeholder': 'last_name','class':'form-control', 'aria-label':'last_name', }), 
            'organization': forms.TextInput(attrs={'placeholder': 'organization','class':'form-control', 'aria-label':'organization', }), 
            'phone' : PhoneNumberPrefixWidget(initial='GB', attrs={'placeholder': 'Enter phone number', 'aria-label':'phone_number'}, number_attrs ={'class':'form-control'} , country_attrs={'class': 'input-group-text'}) ,
            
            'email': forms.EmailInput(attrs={'placeholder': 'email', 'class':'form-control', 'aria-label':'email' , }),     
            
        }
        labels = {                    
            'username':'Username',
            'first_name':'First name',
            'last_name':'Last Name',
            'organization':'Organization',
            'phone':'Phone',
            'email': 'Email',            
        }
        
# custom input typ        
class DateInput(forms.DateInput):
    input_type = 'date'       
   
        
class ProfileForm(forms.ModelForm):
    class Meta:       
        model = Profile
        fields = ('about','location','birthdate',)        
        widgets = {                      
            'about': forms.Textarea(attrs={'placeholder': 'about', 'class':'form-control', 'aria-label':'about', 'style':"height: 150px;" }),
            'location': forms.TextInput(attrs={'placeholder': 'location', 'class':'form-control', 'aria-label':'location' }),
            'birthdate': DateInput(attrs={'data-datepicker': "" , 'class':'form-control', 'aria-label':'birthdate', }),            
            
        }
        labels = {                         
            'about': 'About',
            'location': 'Location',
            'birthdate': 'Birth Day', 
        }


class SetPasswordForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)        
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class':'form-control', "placeholder": "New Password"})
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class':'form-control', "placeholder": "Confirm Password"})
        
        
        
class PasswordResetForm(PasswordResetForm):

    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)        
        self.fields['email'].widget = forms.EmailInput(attrs={ 'class':'form-control', "placeholder": "E-mail address"}) 
        
        


class PasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget = forms.PasswordInput(attrs={'autocomplete': 'current-password', 'autofocus': True, 'class':'form-control', "placeholder": "Old Password"})
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class':'form-control', "placeholder": "New Password"})
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class':'form-control', "placeholder": "Confirm New Password"})
        
        

class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = '__all__'
        
      
        
class UserCreationFormFront(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields['username'].widget.attrs[
                "autofocus"
            ] = True
        
    username = forms.CharField(label = 'Username', widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "Username",   }))
    email = forms.EmailField(label = 'E-Mail Address', widget=forms.EmailInput(attrs={"class": "form-control form-control-lg", "placeholder": "Email Address"}))
    password1 = forms.CharField(label = 'Password', widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg", "placeholder": "Password" }))
    password2 = forms.CharField(label = 'Confirm Password', widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg", "placeholder": "Confirm Password"}))
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)   
    
    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password1')
        
        if email and password:
            email_qs = User.objects.filter(email=email)
            if not email_qs.exists():
                pass    
            else:               
                is_active_qs = User.objects.filter(email=email, is_active=False).first()          
                if is_active_qs:    
                    subject = 'Account activation required!'  
                    current_site = Site.objects.get_current()  
                    message = render_to_string('emails/account_activation_email.html', {
                        'user': is_active_qs,                    
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(is_active_qs.pk)),
                        'token': account_activation_token.make_token(is_active_qs),                        
                    })
                    
                    is_active_qs.email_user(subject, message)                   
                    raise forms.ValidationError(f'You have an account already with this email. An account activation link has been sent to your mailbox {email}')
        return super(UserCreationFormFront, self).clean(*args, **kwargs)    

class UserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'
        
 
class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'remember_me']    
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the placeholder attribute dynamically
        self.fields['username'].widget.attrs['placeholder'] = self.fields['username'].label   
        self.fields['password'].widget.attrs['placeholder'] = 'Password'  
        self.fields['username'].label= ''   
        self.fields['password'].label= '' 
        self.fields['captcha'].label= '' 
             
        
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "autofocus":"" }))    
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg"}))
    remember_me = forms.BooleanField(initial=False,  required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)     
    
    def clean(self, *args, **kwargs):        
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if email and password:
            email_qs = User.objects.filter(email=email)
            if not email_qs.exists():
                raise forms.ValidationError("The user does not exist")
            else:
                is_active_qs = User.objects.filter(email=email, is_active=False).first()
                if is_active_qs:
                    subject = 'Account activation required!'  
                    current_site = Site.objects.get_current()  
                    message = render_to_string('emails/account_activation_email.html', {
                        'user': is_active_qs,                    
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(is_active_qs.pk)),
                        'token': account_activation_token.make_token(is_active_qs),                        
                    })
                    
                    is_active_qs.email_user(subject, message)                      
                    raise forms.ValidationError(f'Account is not active, your need to activate your account before login. An account activation link has been sent to your mailbox {email}')                
                else:
                    user = authenticate(email=email, password=password)      
                    if not user:
                        raise forms.ValidationError("Incorrect password. Please try again!")    
        else:
            raise forms.ValidationError("Add you credentials!") 
                                           
        return super(LoginForm, self).clean(*args, **kwargs)
    
class AddressForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.fields['country'].widget.choices = [('', '(Please select a country)')] + [(code, name) for code, name in countries]
        self.fields['country'].widget.attrs = {'class':'form-select', 'placeholder': 'Country'}
        


    class Meta:
        model = Address
        fields = ['name', 'street_address', 'city','country', 'postal_code', 'phone']
        
        
        
        widgets = {
            'name' : forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Enter Address Name'}),
            'street_address' : forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Street Address'}),
            'city' : forms.TextInput(attrs={'class':'form-control', 'placeholder': 'City'}),
            'postal_code' : forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Postal code'}),
            # 'country': CountrySelectWidget(attrs={'class':'form-select', 'empty_label' : 'sssssssssssss'}),
            # 'country' : forms.Select(attrs={'class':'form-select', 'placeholder': 'Country', 'empty_label': '(Please select a country)'}),          
            'phone' : PhoneNumberPrefixWidget(initial='BD', attrs={'placeholder': 'Enter phone number', 'aria-label':'phone_number'}, number_attrs ={'class':'form-control'} , country_attrs={'class': 'input-group-text'})
        }
        labels = {
            'name' : '',
            'street_address' : '',
            'city' : '',
            'postal_code' : '',
            'country' : '',          
            'phone' : ''
        }
    
    
class ExpertProfileForm(forms.ModelForm): 
    def __init__(self, user, *args, **kwargs):       
        super(ExpertProfileForm, self).__init__(*args, **kwargs)
        self.user = user
    
  
    
    class Meta:      
        model = ExpertiesProfile
        fields = '__all__'
        exclude = ('user',)
        
        widgets = {
            'expert_type' : forms.Select(attrs={
                'class': 'bg-transparent border rounded-0 border-1 form-select form-select-lg input-color-form w-100',         
                'id': 'expert_type',
                'placeholder' : 'Select Expert Type'
            }),
            'skills' : forms.SelectMultiple(attrs={
                'class': 'bg-transparent border rounded-0 border-1 form-select form-select-lg input-color-form w-100',
                'multiple': "multiple",
                'id': 'select_skills',
                'placeholder' : 'Select Skills'
            }),
            'experience_years' : forms.TextInput(attrs={
                'class': 'bg-transparent border rounded-0 border-1 input-color-form w-100',
                'id': 'experience_years',
                'placeholder' : 'Write years of experience eg: 10'
            }),
            'title' : forms.TextInput(attrs={
                'class': 'bg-transparent border rounded-0 border-1 input-color-form w-100',
                'id': 'title',
                'placeholder' : 'Enter title'
            }),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        user = self.user
        expert_type = cleaned_data.get('expert_type')    
        
        if self.instance.pk:            
            if self.instance.has_approved:
                get_approved = self.instance.expertise_profile_approval_request.all()
                for ar in get_approved:                   
                    if ar.is_approved:                        
                        ar.status = ApprovalStatus.objects.get(title="modified")
                        ar.save()
        
        # Check if the user already has an ExpertiesProfile with the same expert_type
        existing_profiles = ExpertiesProfile.objects.filter(user=user, expert_type=expert_type).exclude(pk=self.instance.pk if self.instance else None)

        if existing_profiles.exists():
            raise forms.ValidationError(f'You have already posted an Expertise Profile with {expert_type} expert type.')

        # Check if the user already has 4 ExpertiseProfiles
        total_profiles = ExpertiesProfile.objects.filter(user=user).count()
        if total_profiles >= 4:
            raise forms.ValidationError('You have reached the maximum limit of Expertise Profiles.')

        return cleaned_data
    
    
class ExpertProfileApprovalRequestForm(forms.ModelForm): 
    def __init__(self, ex_profile, *args, **kwargs):           
        super(ExpertProfileApprovalRequestForm, self).__init__(*args, **kwargs)
        self.ex_profile = ex_profile
    
    class Meta:      
        model = ExpertProfileApprovalRequest
        fields = '__all__'
        exclude = ('expert_profile','status','office_remarks')
        
        widgets = {
            
            'doc_title' : forms.TextInput(attrs={
                'class': 'bg-transparent border rounded-0 border-1 form-control input-color-form w-100',
                'id': 'doc_title',
                'placeholder' : 'Document Title'
            }),
            'suporting_doc' : forms.FileInput(attrs={
                'class': 'bg-transparent border rounded-0 border-1 form-control input-color-form w-100',
                'id': 'suporting_doc',
                'placeholder' : 'Upload File'
            }),
            'suporting_url' : forms.TextInput(attrs={
                'class': 'bg-transparent border rounded-0 border-1 form-control input-color-form w-100',
                'id': 'sourcing_url',
                'placeholder' : 'Enter URL'
            }),
            'description' : forms.Textarea(attrs={
                'class': 'bg-transparent border rounded-0 border-1 form-control input-color-form w-100',
                'id': 'description',
                'placeholder' : 'Descriptions',
                'rows' : 10
            }),
        }
        
    def clean(self):        
        cleaned_data = super().clean()        
        if self.ex_profile.expertise_profile_approval_request.all().count() >= settings.MAXIMUM_APPROVAL_REQUEST_ALLOWED:
            raise forms.ValidationError('You have reached the maximum limit of Approval Request.')
        return cleaned_data
    
    
    
class UserVerificationRequestForm(forms.ModelForm): 
    def __init__(self, request, *args, **kwargs):           
        super(UserVerificationRequestForm, self).__init__(*args, **kwargs)
        self.request = request
    
    class Meta:      
        model = UserVerificationRequest
        fields = '__all__'
        exclude = ('user','status','office_remarks')
        
        widgets = {
            
            
            'id_proof' : forms.FileInput(attrs={
                'class': 'bg-transparent border rounded-0 border-1 form-control input-color-form w-100',
                'id': 'id_proof',
                'placeholder' : 'Upload ID Proof'
            }),
            
            'address_proof' : forms.FileInput(attrs={
                'class': 'bg-transparent border rounded-0 border-1 form-control input-color-form w-100',
                'id': 'address_proof',
                'placeholder' : 'Upload Address Proof'
            }),
            
        }
        
    def clean(self):        
        cleaned_data = super().clean()    
        return cleaned_data
    
    
class InteractionForm(forms.ModelForm):
    def __init__(self, request, *args, **kwargs):           
        super(InteractionForm, self).__init__(*args, **kwargs)
        self.request = request
        
        
        
    class Meta:      
        model = Interactions
        fields = '__all__'
        exclude = ('todo', 'waited_for_reply', 'user', 'ans_required','reply_accepted')
        
        widgets = {            
            'body' : forms.Textarea(attrs={
                'class': 'bg-transparent border border-1 form-control input-color-form w-100 ',
                'id': 'id_body',
                'placeholder' : 'Write Interaction here....',
                'rows' : 5
            }),   
        }
        labels = {
            'body' : ''
        }
        
        
    def clean(self):        
        cleaned_data = super().clean()   
        return cleaned_data    
    
    def save(self, commit=True):
        instance = super(InteractionForm, self).save(commit=False)

        if commit:
            instance.save()

            if instance.user_is_project_customer:
                if instance.previous_interaction and instance.previous_interaction.user_is_project_customer:
                    instance.previous_interaction.waited_for_reply = 0
                instance.waited_for_reply = instance.awaiting
                instance.ans_required = False  # Important

            if instance.user_is_project_contributor:          
                if instance.has_ans_required_but_not_replied_in_previous:
                    instance.ans_required = False  # Important 
                else:
                    # For the first-time entry for the instance, set ans_required to True
                    instance.ans_required = True  # Important    

            instance.save()   
                                            
        return instance

    
    


