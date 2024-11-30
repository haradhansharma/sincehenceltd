from django.conf import settings
from django.shortcuts import redirect, render

from core.context_processor import site_data
from core.helper import custom_send_mass_mail
from core.tasks import send_mass_mail_task
from .forms import *
from django.contrib import messages

def contact(request):
    
    template_name = 'contact/contact.html' 
    form = ContactUsForm()
    
    site = site_data()
    site['title'] = 'Our Contact Address Here.'
    site['description'] = f'Contact {site.get("name")} for any inquiries, feedback, or collaboration opportunities. Our dedicated team is here to assist you. Reach out to us through the provided contact details or fill out the contact form on our page. We look forward to hearing from you and providing the support you need.'
    
    
    context = {       
        'site_data' : site
    }
        
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            form.save()            
            messages.success(request, 'Your message has been sent. We will get back to you soon.')
        
            email_messages = []
            
            from_email = settings.DEFAULT_FROM_EMAIL               
            
            # Send email to the site admin
            admin_subject = f'SINCEHENCE LTD - New contact form submission'
            admin_message = f"Name: {form.cleaned_data['name']}\nEmail: {form.cleaned_data['email']}\n\nMessage: {form.cleaned_data['message']}"        
            admin_reply_to = [form.cleaned_data['email']]        
            admin_mail = [site_data().get('email')]
            
            
            email_messages.append((admin_subject, admin_message, from_email, admin_mail , '',  admin_reply_to, ''))
            
            visitor_subjct = f"SINCEHENCE LTD - Greetings from {form.cleaned_data['name']}!" 
            visitor_message = f"Dear {form.cleaned_data['name']},\n\nThank you for reaching out to us through our website." 
            visitor_message += f"We appreciate your interest in {site_data().get('name')}!\n\n"
            visitor_message += f"This email is to acknowledge that we have received your contact form submission. Please note that this is a no-reply email, "
            visitor_message += f"so there's no need to reply to it.\n\nOur team is currently reviewing your message, and we will get back to you soon with a response. "
            visitor_message += f"We strive to provide excellent service and address your inquiry promptly.\n\nOnce again, we thank you for getting in touch with us. "
            visitor_message += f"We look forward to connecting with you!\n\nBest regards,\nThe {site_data().get('name')} Team"
            visitor_mail = [form.cleaned_data['email']]
            
            email_messages.append((visitor_subjct, visitor_message, from_email, visitor_mail, '', '', ''))        

            send_mass_mail_task.delay(email_messages, fail_silently=False) 
             
            return redirect(request.path)
            
            
        else:  
            context.update({'form':form}) 
            messages.error(request, 'There was an error with your submission. Please try again.')
            
            return render(request, template_name, context=context)
       
    
    context.update({'form':form})  
    
    return render(request, template_name, context=context)

