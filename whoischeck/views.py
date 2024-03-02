import json
import os
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from core.context_processor import site_data
from whoischeck.forms import DomainForm
from whoischeck.models import WhoisResult
from django.contrib import messages
from django.core.cache import cache
from django.templatetags.static import static
import logging
log =  logging.getLogger('log')
import whois21
from django.template.loader import get_template

def process_result(result):
    if isinstance(result, list):
        # Convert the list to a set to make it unique, then convert it back to a list
        unique_list = list(set(result))
        # Join the elements of the list with commas
        return ', '.join(map(str, unique_list))
    else:
        return result

# Create your views here.
def check_whois(request):

    template = 'whois/home.html'     
    
    path_domain = request.GET.get('dm')     
    
    site = site_data()
    
    if path_domain:
        site['title'] = f'Whois Lookup RADP record for {path_domain}'   
        site['description'] = f'Verified registration info for domain {path_domain} with our free WHOIS lookup service. '
    else: 
        site['title'] = 'Lookup RADP WHOIS Domain'          
        site['description'] = 'Unlock verified registration info with our free WHOIS lookup service. Discover ownership details, reg history & more for any domain. Trust us for accuracy.'
    site['og_image'] = request.build_absolute_uri(static('assets/img/whois_radp.jpg'))
    
    faq_path = 'whois/faq.json' 
    faq_template = get_template(faq_path)
    faq_data = json.loads(faq_template.render())
    
    context = {    
        'site_data' : site,   
        'faq_data' : faq_data       
    }     
    
    if request.method == 'POST':
        form = DomainForm(request.POST)
        
        if form.is_valid():
            domain_name = form.cleaned_data['domain_name']
        else:
            # return form with error
            context.update({'form': form})
            return render(request, template, context)        
        
        # check if data in cache
        domain_data = cache.get(f'domain_data_{domain_name}')  
                        
        if domain_data is not None:      
            # As get request checking cache, so just redirect here to the get request   
            return redirect(reverse('whoischeck:check_whois') + f'?dm={domain_name}') 
        else:    
            wq = whois21.WHOIS(domain_name)        
            if not wq.success:
                messages.warning(request, 'Error happened! Please try again later!')
                log.warning(f'Warning:{wq.error}')
                return redirect(reverse('whoischeck:check_whois') + f'?dm={domain_name}') 
  
            fetched_domain = process_result(wq.whois_data.get('DOMAIN NAME'))
            registrar = process_result(wq.whois_data.get('REGISTRAR'))
            registrant_name = process_result(wq.whois_data.get('REGISTRANT NAME'))
            registrant_organization = process_result(wq.whois_data.get('REGISTRANT ORGANIZATION'))
            registrant_street = process_result(wq.whois_data.get('REGISTRANT STREET'))
            registrant_city = process_result(wq.whois_data.get('REGISTRANT CITY'))
            registrant_state = process_result(wq.whois_data.get('REGISTRANT STATE/PROVINCE'))
            registrant_postal = process_result(wq.whois_data.get('REGISTRANT POSTAL CODE'))
            registrant_country = process_result(wq.whois_data.get('REGISTRANT COUNTRY'))            
            registrant_email = process_result(wq.whois_data.get('REGISTRANT EMAIL'))           
            creation_date = process_result(wq.whois_data.get('CREATION DATE'))
            updated_date = process_result(wq.whois_data.get('UPDATED DATE'))
            expiration_date = process_result(wq.whois_data.get('REGISTRY EXPIRY DATE'))
            registry_domain_id = process_result(wq.whois_data.get('REGISTRY DOMAIN ID'))
            name_server = process_result(wq.whois_data.get('NAME SERVER'))
            domain_status = process_result(wq.whois_data.get('DOMAIN STATUS'))         
            
            
            
            
            domain_whois = {}            
            #domain Info
            domain_info = {
                'DOMAIN NAME' : fetched_domain,
                'REGISTRY DOMAIN ID' : registry_domain_id,            
                'REGISTRAR' : registrar,                          
                'CREATION DATE' : creation_date,
                'REGISTRY EXPIRY DATE' : expiration_date,
                'UPDATED DATE' : updated_date,
                'NAME SERVER' : name_server,
                'DOMAIN STATUS' : domain_status,
            }
            
            # registrant contact
            registrant_contact = {
                'REGISTRANT NAME' : registrant_name,    
                'REGISTRANT ORGANIZATION' : registrant_organization, 
                'REGISTRANT STREET' : registrant_street, 
                'REGISTRANT CITY' : registrant_city, 
                'REGISTRANT STATE/PROVINCE' : registrant_state, 
                'REGISTRANT POSTAL CODE' : registrant_postal, 
                'REGISTRANT COUNTRY' : registrant_country, 
                'REGISTRANT EMAIL' : registrant_email, 
            } 
            
            raw_data = {
                'raw_data' : wq.raw.decode('utf-8')
            }               
            
            
            domain_whois.update({
                'domain_info' : domain_info,
                'registrant_contact' : registrant_contact,
                'raw_data' : raw_data                    
            })
            
            domain_data = domain_whois
            
            # if no cache found we will keep record of each time whois query          
            new_whois = WhoisResult(
                domain_name = domain_name,
                registrar = registrar,
                registrant_name = registrant_name,
                registrant_organization = registrant_organization,
                name_server = name_server,
                creation_date = creation_date,
                updated_date = updated_date,
                expiration_date = expiration_date,                
            )  
     
            new_whois.save()
            
            # Set cache
            cache.set(f'domain_data_{domain_name}', domain_data, timeout = 60 * 60)   
            return redirect(reverse('whoischeck:check_whois') + f'?dm={domain_name}') 
        
    else:    
        
        if path_domain is not None:        
            form = DomainForm(initial={'domain_name': path_domain})
        else:
            form = DomainForm()
           
        # Always Take data from cache 
        domain_data = cache.get(f'domain_data_{path_domain}')  
        
        context.update({'form': form, 'results': domain_data})
        return render(request, template, context)