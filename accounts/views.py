from datetime import datetime
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import Http404, HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from calendar_app.helpers import get_offdays
from calendar_app.models import OffDay
from core.helper import user_activities, user_comments
from service.helpers import get_project_created
from service.models import Order, ProjectTodo
from service.decorators import customer_or_contributor_required
from .models import *
from .forms import *
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .tokens import account_activation_token
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView, PasswordChangeDoneView
from core.context_processor import site_data
from django.contrib.auth import update_session_auth_hash
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import CreateView

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_activities, all_activities = user_activities(self.request)
        context['latest_activities'] = latest_activities
        return context

@login_required
def delete_avatar(request):    
    user = request.user
    profile = user.get_profile
    profile.avatar.delete()
    profile.avatar = ''
    profile.save()    
    return HttpResponseRedirect(reverse('accounts:profile_setting', args=[str(user.id)]))

@login_required
def profile_setting(request):  
    
    
    site = site_data() 
    site['title'] = f'Profile Settings'
    site['description'] = f'Take control of your online presence with our profile settings page. Customize your profile, privacy settings, and communication preferences to tailor your experience. Safeguard your data and manage your interactions effortlessly. Unlock the power of personalization at your fingertips'
    
      
    
    context = {
        "user":request.user,         
        'site_data' : site ,               
    } 
    
    latest_activities, all_activities = user_activities(request)
    context['latest_activities'] = latest_activities   
    
     
    if request.method == "POST":

        print(request.POST, request.FILES)
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)   
        avatar_form = AvatarForm(request.POST, request.FILES, instance=request.user.profile)
        	
        if 'user_form' in request.POST:   
            if user_form.is_valid():                
                user_form.save()
                messages.success(request,('Your profile was successfully updated!'))                
            else:
                messages.error(request, 'Invalid form submission.')     
                return redirect(reverse('accounts:profile_setting'))           
              
                
        if 'profile_form' in request.POST:            	    
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request,('Your profile data was successfully updated!'))
            else:
                messages.error(request, 'Invalid form submission.')
                return redirect(reverse('accounts:profile_setting'))    
               
                
        if 'avatar_form' in request.POST or 'avatar_form' in request.FILES:          
            if avatar_form.is_valid():
                avatar_form.save()
                messages.success(request,('Avatar Updated successfully!'))
            else:
                messages.error(request, 'Invalid form submission.')
                return redirect(reverse('accounts:profile_setting'))    
        
                
        context.update({'user_form' : user_form})
        context.update({'profile_form' : profile_form})
        context.update({'avatar_form' : avatar_form})   
                
        response = render(request, 'registration/account_settings.html', context = context)
        response['X-Robots-Tag'] = 'noindex, nofollow'
        return response 
                
    
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)    
    avatar_form = AvatarForm(instance=request.user.profile)     
    
    context.update({'user_form' : user_form})
    context.update({'profile_form' : profile_form})
    context.update({'avatar_form' : avatar_form})   
    
    
    response = render(request, 'registration/account_settings.html', context = context)
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response 

@login_required
def password_change(request):        
    from django.contrib.auth import logout
    site = site_data()     
    site['title'] = 'Change Password'
    site['description'] = 'Securely update your password on our platform. Protect your account with a new, strong password to ensure the safety of your personal information. Change password hassle-free and strengthen your online security today.'
    
    
    context = {
        "user":request.user,
        'site_data' : site ,
    }
    
    if request.method == "POST":        
        password_form = PasswordChangeForm(user=request.user, data=request.POST)        
        if password_form.is_valid():            
            password_form.save()            
            update_session_auth_hash(request, password_form.user)            
            messages.success(request,('Your password was successfully updated!')) 
            logout(request)
            return redirect(reverse("accounts:password_change_done"))
        else:
            context.update({           
                "form":password_form,               
            })    
                    
            response = render(request, 'registration/password_change_form.html', context = context)
            response['X-Robots-Tag'] = 'noindex, nofollow'
            return response   
    
    password_form = PasswordChangeForm(request.user)   
    context.update({           
                "form":password_form,               
            })
    latest_activities, all_activities = user_activities(request)
    context['latest_activities'] = latest_activities
        
    response = render(request, 'registration/password_change_form.html', context = context)
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response 


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    
   
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books 
        site = site_data()    
        site['title'] = 'Password reset completed'     
        site['description'] = 'Password reset successfully! Your account is now secure. Log in with your new credentials and regain access to your account. Stay protected with our secure password management tools.'     
        

        context['site_data'] = site
        # Create an HttpResponse object with your template
        response = self.render_to_response(context)

        # Set the X-Robots-Tag header in the HttpResponse object
        response['X-Robots-Tag'] = 'noindex, nofollow'
        return context
    

class CustomPasswordResetView(PasswordResetView):
    from .forms import PasswordResetForm
    
    #overwriting form class to take control over default django
    form_class = PasswordResetForm
    success_url = reverse_lazy("accounts:password_reset_done")
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        site = site_data()   
        site['title'] = 'Reset your password'
        site['description'] = 'Reset your password securely and regain access to your account with our user-friendly password reset form. Safeguard your data and follow a simple step-by-step process to create a new password. Experience hassle-free account recovery and ensure the protection of your valuable information. Reset your password now and get back to enjoying our platform with peace of mind'

        context['site_data'] = site
        # Create an HttpResponse object with your template
        response = self.render_to_response(context)

        # Set the X-Robots-Tag header in the HttpResponse object
        response['X-Robots-Tag'] = 'noindex, nofollow'
        return context
    

class CustomPasswordResetDoneView(PasswordResetDoneView):
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        site = site_data()   
        site['title'] = 'Password reset done'
        site['description'] = 'Password Reset Done - Your password has been successfully reset. '

        context['site_data'] = site
        # Create an HttpResponse object with your template
        response = self.render_to_response(context)

        # Set the X-Robots-Tag header in the HttpResponse object
        response['X-Robots-Tag'] = 'noindex, nofollow'
        return context
    

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    from .forms import SetPasswordForm
    success_url = reverse_lazy("accounts:password_reset_complete")
    #overwriting form class to take control over default django
    form_class = SetPasswordForm
    
    def get_context_data(self, **kwargs):
        
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books  
        
        site = site_data()   
        site['title'] = 'Password reset confirm'
        site['description'] = 'Confirm your password reset. '

        context['site_data'] = site
        # Create an HttpResponse object with your template
        response = self.render_to_response(context)

        # Set the X-Robots-Tag header in the HttpResponse object
        response['X-Robots-Tag'] = 'noindex, nofollow'
        
        return context
    
class CustomLoginView(LoginView):
    from .forms import LoginForm 
    
    
    
    
    form_class = LoginForm
    success_url = reverse_lazy('accounts:user_dashboard')  # Replace with your success URL name

    def form_valid(self, form):
        # Handle the "Remember Me" option
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            # Set session expiry to 0 seconds to close the session after the browser is closed
            self.request.session.set_expiry(0)
            # Set session as modified to force data updates/cookie to be saved
            self.request.session.modified = True

        # Set the term_accepted session variable
        self.request.session['term_accepted'] = True

        # Call the parent class's form_valid method
        return super(CustomLoginView, self).form_valid(form)

    def form_invalid(self, form):
        # Handle the case when the form is invalid
        # You can add custom logic here if needed    
        messages.error(self.request, 'Invalid form submission.')   
        return super(CustomLoginView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # Add your additional context data here, such as 'site_data'
        site = site_data()
        site['title'] = 'Unlock Your World of Possibilities - Log In Now!'
        site['description'] = 'Welcome to our login page - where your online journey begins. Log in to access a world of personalized features and exclusive benefits. Securely manage your account and explore a seamless online experience. Join us today!'
        context['site_data'] = site
      

        # Set the X-Robots-Tag header in the HttpResponse object
        self.response = self.render_to_response(context)
        self.response['X-Robots-Tag'] = 'index, follow'
        
        if settings.SALING_SERVICE:
            pass
        else:
            raise Http404

        return context

    


from django.contrib.messages.views import SuccessMessageMixin  
class SignupView(SuccessMessageMixin, CreateView):
    
    model = User  # Use your custom User model
    form_class = UserCreationFormFront  # Use Django's built-in UserCreationForm or your custom form
    template_name = 'registration/signup.html'  # Create a template for the signup form
    success_url = reverse_lazy('accounts:login')  # Redirect to the login page upon successful registration
    success_message = 'Please confirm your email to complete registration.'

    def form_valid(self, form):
        # Save the user object and log the user in upon successful registration
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        current_site = get_current_site(self.request)
        subject = 'Account activation required!'
        message = render_to_string('emails/account_activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })

        user.email_user(subject, message)

        return super().form_valid(form)

    def form_invalid(self, form):
        # Handle the case when the form is invalid
        # You can add custom logic here and customize the error messages
        messages.error(self.request, 'Invalid form submission.')
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        # Handle the case when a logged-in user tries to access the signup page
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('accounts:user_dashboard'))  # Redirect to the dashboard page
        return super().get(request, *args, **kwargs)

    
    
    def get_context_data(self,  **kwargs):
        
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        

        site = site_data()   
        site['title'] = 'Unlock Your World of Possibilities - Signup Now!'
        site['description'] = 'Welcome to our signup page - where your online journey begins. Sign up to access a world of personalized features and exclusive benefits. Securely manage your account and explore a seamless online experience. Join us today!'

        context['site_data'] = site
        # Create an HttpResponse object with your template
        response = self.render_to_response(context)

        # Set the X-Robots-Tag header in the HttpResponse object
        response['X-Robots-Tag'] = 'index, follow'
        
        if settings.SALING_SERVICE:
            pass
        else:
            raise Http404
        return context
    
   


def activate(request, uidb64, token):
    if settings.SALING_SERVICE:
        pass
    else:
        raise Http404
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, ('Your account have been confirmed.'))
        return HttpResponseRedirect(reverse_lazy('accounts:login'))
    else:
        messages.warning(request, ('Activation link is invalid!'))
        return HttpResponseRedirect(reverse_lazy('core:home'))
    


from django.views import View

@method_decorator(login_required, name='dispatch')    
class RecentCommentsView(View):
    http_method_names = ['get']
    template_name = 'registration/account_recent_comments.html'
    

    def get(self, request, *args, **kwargs):
        

        context = { 
            'data' : 'data',     
        }
        site = site_data()
        site['title'] = 'service.name'
        site['description'] = 'service.description[:150]'
        
        
        context['site_data'] = site
        
        latest_activities, all_activities = user_activities(request)
        context['latest_activities'] = latest_activities
 
        
        user_blog_comments_latest, user_blog_comments_all = user_comments(request) 
        context['user_blog_comments_all'] = user_blog_comments_all      

        return render(request, self.template_name, context)

    
 
 
 

@method_decorator(login_required, name='dispatch')    
class RecentActivityView(View):
    http_method_names = ['get']
    template_name = 'registration/account_recent_activity.html'
    

    def get(self, request, *args, **kwargs):
        

        context = { 
            'data' : 'data',     
        }
        site = site_data()
        site['title'] = 'service.name'
        site['description'] = 'service.description[:150]'
        
        
        context['site_data'] = site
        
        latest_activities, all_activities = user_activities(request)
        context['latest_activities'] = latest_activities
        context['all_activities'] = all_activities       

        return render(request, self.template_name, context)

  
    
    
@method_decorator(login_required, name='dispatch')    
class ExpertiseProfile(View):
    http_method_names = ['get', 'post']
    template_name = 'registration/account_expert_profiles.html'
    
    def get_object(self, profile_id):        
        try:
            ex_profile = self.request.user.expert_profiles.get(id = profile_id)
            return ex_profile
        except Exception as e:
            raise Http404   
    
    def get_expert_profiles(self):
        expert_profiles = self.request.user.expert_profiles.all()
        return expert_profiles   

    def get(self, request, *args, **kwargs):
        expert_profiles = self.get_expert_profiles()
                
        if request.user.has_approved:
            pass
        else:
            messages.warning(request, 'You are not verified yet! Submit verification request.')
            return HttpResponseRedirect(reverse('accounts:verification_request'))        
        
        
        form = ExpertProfileForm(user=request.user)
        context = { 
            'expert_profiles' : expert_profiles,     
            'form' : form,
            'action_url' : reverse('accounts:expert_profiles'),
            'btn_text' : 'Create'
        }
        site = site_data()
        site['title'] = 'service.name'
        site['description'] = 'service.description[:150]'
        
        context['site_data'] = site
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        ex_profile_id = kwargs.get('profile_id')    
          
        if ex_profile_id:
            obj = self.get_object(ex_profile_id)
            form = ExpertProfileForm(user=request.user, data=request.POST, instance=obj)
        else:
            form = ExpertProfileForm(user=request.user, data=request.POST, instance=None)
    
        method = request.POST.get('_method')
        if method == 'DELETE' and ex_profile_id:
            obj.delete()
            # Refresh expert_profiles after delete
            expert_profiles = self.get_expert_profiles()
            context = { 'expert_profiles': expert_profiles }
            return render(request, 'registration/ex_profile_blocks.html', context) 
        elif method == 'EDIT' and ex_profile_id:
            form = ExpertProfileForm(user=request.user, instance=obj)
            context = { 
                       'form': form, 
                       'action_url' : reverse('accounts:edit_expert_profile', kwargs={'profile_id' :  ex_profile_id}),
                       'btn_text' : 'Save'
                       }
            return render(request, 'registration/ex_profile_form.html', context) 
        
        else:  
            expert_profiles = self.get_expert_profiles()  
            if request.user.has_approved:
                pass
            else:
                messages.warning(request, 'You are not verified yet! Submit verification request. To do so, click on "Developer" link from footer!')
                context = { "form": form,'expert_profiles': expert_profiles  }
                return render(request, 'registration/ex_profile_blocks.html', context)           
            
            if form.is_valid():               
                instance = form.save(commit=False)             
                instance.user = self.request.user        
                instance.save()
                form.save_m2m()
                # Refresh expert_profiles after saving
                expert_profiles = self.get_expert_profiles()
                context = { 'expert_profiles': expert_profiles }
                return render(request, 'registration/ex_profile_blocks.html', context)
            else:            
                context = { "form": form,'expert_profiles': expert_profiles  }
                return render(request, 'registration/ex_profile_blocks.html', context)
                
            
@method_decorator(login_required, name='dispatch')    
class SubmitApprovalRequest(View):
    http_method_names = ['get', 'post']
    template_name = 'registration/account_expert_profile_approval_rquests.html'
    
    def get_object(self, profile_id):        
        try:
            ex_profile = self.request.user.expert_profiles.get(id = profile_id)
            return ex_profile
        except Exception as e:
            raise Http404   
    
    def get_expert_profiles(self):
        expert_profiles = self.request.user.expert_profiles.all()      
        return expert_profiles   
    
    def ge_all_requests(self, ex_profile_id):
        return self.get_object(ex_profile_id).expertise_profile_approval_request.all()
  

    def get(self, request, *args, **kwargs):
        
        ex_profile_id =  kwargs.get('profile_id')
 
        all_requests = self.ge_all_requests(ex_profile_id)
        
        form = ExpertProfileApprovalRequestForm(ex_profile = self.get_object(ex_profile_id))     
        
        context = { 
            'all_requests' : all_requests,    
            'form' : form,
            'action_url' : reverse('accounts:submit_approval_request', kwargs={'profile_id' : ex_profile_id}),
            'btn_text' : 'Create'
        }
        site = site_data()
        site['title'] = 'service.name'
        site['description'] = 'service.description[:150]'
        
        context['site_data'] = site
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs): 
        
        ex_profile_id =  kwargs.get('profile_id')
     
        action_url = reverse('accounts:submit_approval_request', kwargs={'profile_id' : ex_profile_id}) 
        method = request.POST.get('_method')
        context = {              
            'btn_text' : 'Create', 
            'action_url' : action_url,     
        }
        
        if method == 'DELETE' and ex_profile_id:
            ex_profile_approval_request_id = kwargs.get('request_id')  
            obj_to_delete = ExpertProfileApprovalRequest.objects.get(id=ex_profile_approval_request_id)
            obj_to_delete.suporting_doc.delete(save=False)  
            obj_to_delete.delete()
            # Refresh expert_profiles after saving       
            all_requests = self.ge_all_requests(ex_profile_id)
            form = ExpertProfileApprovalRequestForm(ex_profile = self.get_object(ex_profile_id))                 
            context.update({"form": form, 'all_requests' : all_requests})
            return render(request, self.template_name, context)
        else:  
            all_requests = self.ge_all_requests(ex_profile_id)      
            if  len(all_requests) >= settings.MAXIMUM_APPROVAL_REQUEST_ALLOWED:
                form = ExpertProfileApprovalRequestForm(ex_profile = self.get_object(ex_profile_id)) 
                error_message = 'You have reached the maximum limit of Approval Requests.'
                messages.warning(request, error_message)
                context.update({'error_message': error_message,"form": form, 'all_requests' : all_requests})
                return render(request, self.template_name, context)
                    
            form = ExpertProfileApprovalRequestForm(ex_profile = self.get_object(ex_profile_id), data=request.POST, files=request.FILES)   
            if form.is_valid():                           
                instance = form.save(commit=False)             
                instance.expert_profile = self.get_object(ex_profile_id)      
                instance.save()   
                # Refresh expert_profiles after saving
                all_requests = self.ge_all_requests(ex_profile_id)
                form = ExpertProfileApprovalRequestForm(ex_profile = self.get_object(ex_profile_id))   
                context.update({"form": form, 'all_requests' : all_requests})
                return render(request, self.template_name, context)
            else:   
                context.update({"form": form, 'all_requests' : all_requests})
                return render(request, self.template_name, context)
            
@method_decorator(login_required, name='dispatch')    
class VerificationRequest(View):
    http_method_names = ['get', 'post']
    template_name = 'registration/submit_verification_request.html'    
    
  

    def get(self, request, *args, **kwargs):       
        
        form = UserVerificationRequestForm(request=request)     
        
        context = {               
            'action_url' : reverse('accounts:verification_request'),
            'btn_text' : 'Submit'
        }
        varification_request = request.user.verification_request_obj
        
        if varification_request is not None:
            context.update({
                'varification_request' : varification_request
            })
        if not varification_request or varification_request.is_rejected:
            context.update({
                'form' : form,
            })
            
            
        
        site = site_data()
        site['title'] = 'service.name'
        site['description'] = 'service.description[:150]'
        
        context['site_data'] = site
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {
            'action_url' : reverse('accounts:verification_request'),
            'btn_text' : 'Submit'
        }
        form = UserVerificationRequestForm(request=request, data=request.POST, files=request.FILES)     
        if form.is_valid():                           
            instance = form.save(commit=False)             
            instance.user = request.user 
            instance.save()           
            context.update({'varification_request' : instance})
            return render(request, 'registration/verification_block.html', context)
        else:     
            varification_request = request.user.verification_request_obj           
            context.update({"form": form, 'varification_request' : varification_request})
            return render(request, 'registration/verification_block.html', context)
    

class Orders:
    def __init__(self, request):        
        self.request = request
    
    def user_admin_or_super(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return True
        return False    
            
    def get_orders(self):
        if self.user_admin_or_super():
            orders = Order.objects.all().order_by('-created_at')
        else:            
            orders = Order.objects.filter(customer = self.request.user).order_by('-created_at')       
        return orders
    
    def get_due_orders(self):
        invoiced_orders = self.get_orders().filter(status__in=settings.PAYMENT_PENDING_STATUS)
        due_orders = [order for order in invoiced_orders if order.pending_amount > 0]
        return due_orders
    
    def get_incomplete_orders(self):
        incomplete_orders = self.get_orders().filter(status__in=settings.INCOMPLETE_STATUS)
        return incomplete_orders
    
    def get_processing_orders(self):
        processing_orders = self.get_orders().filter(status__in=settings.PROCESSING_ORDERS)
        return processing_orders

    
 
 
 

@method_decorator(login_required, name='dispatch')    
class DashboardView(View):
    http_method_names = ['get', 'post']
    template_name = 'registration/dashboard.html'
    
    @property
    def user_order_cls(self):
        cls = Orders(self.request)
        return cls    
   

    def get(self, *args, **kwargs):
        
        
        
       
        due_orders = self.user_order_cls.get_due_orders()
        incomplete_orders = self.user_order_cls.get_incomplete_orders()     
        
        

        context = { 
            'data' : 'data',   
            'due_orders' : due_orders[:10],
            'incomplete_orders' : incomplete_orders[:10]
        }
        site = site_data()
        site['title'] = 'service.name'
        site['description'] = 'service.description[:150]'
        
        
        context['site_data'] = site
        
        latest_activities, all_activities = user_activities(self.request)
        context['latest_activities'] = latest_activities
        context['all_activities'] = all_activities       
        
        user_blog_comments_latest, user_blog_comments_all = user_comments(self.request)
        context['user_blog_comments_latest'] = user_blog_comments_latest
        

        return render(self.request, self.template_name, context)


    
    
@method_decorator(login_required, name='dispatch')    
class DueOrdersView(View):
    http_method_names = ['get']
    template_name = 'registration/account_due_orders.html'
    items_per_page = 10
    
    @property
    def user_order_cls(self):
        cls = Orders(self.request)
        return cls    
   

    def get(self, *args, **kwargs):    
        
       
        due_orders = self.user_order_cls.get_due_orders()
        
        # Pagination
        page_number = self.request.GET.get('page', 1)  # Get the page number from the request query parameters
        paginator = Paginator(due_orders, self.items_per_page)
        
        try:
            paginated_due_orders = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver the first page.
            paginated_due_orders = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            paginated_due_orders = paginator.page(paginator.num_pages)
        
        
        context = { 
            'data' : 'data',   
            'due_orders' : paginated_due_orders,
       
        }
        
        site = site_data()
        site['title'] = 'service.name'
        site['description'] = 'service.description[:150]'
        
        
        context['site_data'] = site
        
        latest_activities, all_activities = user_activities(self.request)
        context['latest_activities'] = latest_activities
        context['all_activities'] = all_activities       
        
        user_blog_comments_latest, user_blog_comments_all = user_comments(self.request)
        context['user_blog_comments_latest'] = user_blog_comments_latest
        
        context['next'] = reverse('accounts:due_orders')
        return render(self.request, self.template_name, context)
    
@method_decorator(login_required, name='dispatch')    
class IncompleteOrdersView(View):
    http_method_names = ['get']
    template_name = 'registration/account_incomplete_orders.html'
    items_per_page = 10
    
    @property
    def user_order_cls(self):
        cls = Orders(self.request)
        return cls    
   

    def get(self, *args, **kwargs):    
        
       
        incomplete_orders = self.user_order_cls.get_incomplete_orders()
        
        # Pagination
        page_number = self.request.GET.get('page', 1)  # Get the page number from the request query parameters
        paginator = Paginator(incomplete_orders, self.items_per_page)
        
        try:
            paginated_incomplete_orders = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver the first page.
            paginated_incomplete_orders = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            paginated_incomplete_orders = paginator.page(paginator.num_pages)
        

        
        
        
        context = { 
            'data' : 'data',   
            'incomplete_orders' : paginated_incomplete_orders,
       
        }
        
        site = site_data()
        site['title'] = 'service.name'
        site['description'] = 'service.description[:150]'
        
        
        context['site_data'] = site
        
        latest_activities, all_activities = user_activities(self.request)
        context['latest_activities'] = latest_activities
        context['all_activities'] = all_activities       
        
        user_blog_comments_latest, user_blog_comments_all = user_comments(self.request)
        context['user_blog_comments_latest'] = user_blog_comments_latest
        
     
        return render(self.request, self.template_name, context)
    
    
@method_decorator(login_required, name='dispatch')    
class OrdersView(View):
    http_method_names = ['get']
    template_name = 'registration/account_orders.html'
    items_per_page = 10
    
    @property
    def user_order_cls(self):
        cls = Orders(self.request)
        return cls    
   

    def get(self, *args, **kwargs):    
        
       
        orders = self.user_order_cls.get_processing_orders()
        
        # Pagination
        page_number = self.request.GET.get('page', 1)  # Get the page number from the request query parameters
        paginator = Paginator(orders, self.items_per_page)
        
        try:
            paginated_orders = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver the first page.
            paginated_orders = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            paginated_orders = paginator.page(paginator.num_pages)
        

        
        
        
        context = { 
            'data' : 'data',   
            'orders' : paginated_orders,
       
        }
        
        site = site_data()
        site['title'] = 'service.name'
        site['description'] = 'service.description[:150]'
        
        
        context['site_data'] = site
        
        latest_activities, all_activities = user_activities(self.request)
        context['latest_activities'] = latest_activities
        context['all_activities'] = all_activities       
        
        user_blog_comments_latest, user_blog_comments_all = user_comments(self.request)
        context['user_blog_comments_latest'] = user_blog_comments_latest
        
     
        return render(self.request, self.template_name, context)


    
    
    
@method_decorator(login_required, name='dispatch')    
@method_decorator(customer_or_contributor_required(model_type ='service.order'), name='dispatch')   
class OrderDetails(View):
    http_method_names = ['get', 'post']
    template_name = 'registration/order_details.html'
    

    def get(self, request, *args, obj=None, **kwargs):
        '''
        obj comes from customer_required decorator of service app
        '''
        
        events = [] 
        
        offdays = get_offdays()
        
        for day in offdays:
            events.append(              
                {
                'start': day.selected_date.strftime('%Y-%m-%d'),
                'end': day.selected_date.strftime('%Y-%m-%d'),
                'overlap': 'false',
                'display': 'background',
                'color': '#ff9f89',
                'description' : day.description,
                'title' : 'Holiday'
                }                
            )
            
        milestones = obj.order_project.project_todo.all()
        
        
        for milestone in milestones:
            events.append({
                'title': milestone.milestone, 
                'url': f'#issue{milestone.id}',
                'start': get_project_created(milestone).strftime('%Y-%m-%d'),
                'end': milestone.target_date.strftime('%Y-%m-%d'),
                'description' : milestone.description, 
            
            })
       
        interaction_form = InteractionForm(request=request)
        
        context = { 
            'order' : obj,     
            'milestones' : milestones,
            'events' : events,
            'interaction_form' : interaction_form      
        }
        site = site_data()
        site['title'] = 'service.name'
        site['description'] = 'service.description[:150]'
        
        
        context['site_data'] = site
        
        latest_activities, all_activities = user_activities(self.request)
        context['latest_activities'] = latest_activities
        context['all_activities'] = all_activities    

        return render(request, self.template_name, context)

    def post(self, request, *args, obj=None, **kwargs):
        milestone_id = kwargs.get('todo_id')
        order_id = kwargs.get('pk')
        todo_obj = get_object_or_404(ProjectTodo, id = milestone_id)
  
        if milestone_id:            
            method = request.POST.get('_method')        
            if method:
                if method == 'REPLY_ACCEPT':                                    
                    interaction_id = kwargs.get('interaction_id')
                    interaction_obj = Interactions.objects.get(id=interaction_id)
                    
                    context = {
                        'order' : obj,
                        'milestone' : todo_obj,
                        'interaction' : interaction_obj
                    }
                    
                    
                    if interaction_obj.user_is_project_contributor or request.user.is_staff or request.user.is_superuser:
                        interaction_obj.reply_accepted = True
                        interaction_obj.save()
                    else:
                        context.update({'err_msg': 'Operation Not Permitted!'})
                        
                    
                    return render(request, 'registration/interactions_ans_required.html', context)
            
            
            interaction_form = InteractionForm(request=request, data=request.POST, files=request.FILES)
            if interaction_form.is_valid():
                interaction = interaction_form.save(commit=False)
                interaction.todo = todo_obj
                interaction.user = request.user
                interaction_form.save()   # here call of form is important
                    
                interaction_form = InteractionForm(request=request)
                context = {
                    'order' : obj,
                    'milestone' : todo_obj,
                    'interaction_form' : interaction_form                          
                }
            else:
                context = {
                    'order' : obj,
                    'milestone' : todo_obj,
                    'interaction_form' : interaction_form                         
                }
                
                
            return render(request, 'registration/milestone_block.html', context)
                
                
                
            

  
    

        
    




    
    
    
    
    
    
    

