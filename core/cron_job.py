from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django_cron import CronJobBase, Schedule
from core.helper import build_full_url, custom_send_mail, custom_send_mass_mail
from service.models import Order, OrderInvoice, Quotation
from shcurrency.models import Currency
import requests
import json
from django.db import models
from django.template.loader import render_to_string
from django.db.models import F
from django.utils.safestring import mark_safe
from celery import shared_task
import logging
log =  logging.getLogger('log')

@shared_task
def update_currency(): 
    base = settings.DEFAULT_CURRENCY_CODE
    app_id = settings.OPEN_EXCHANGE_APP_ID
    url = f"https://openexchangerates.org/api/latest.json?app_id={app_id}&base={base}"
    response = requests.get(url)

    if not base:
        log.warning('No default currency found! Cannot update the database!')
        return

    if response.status_code == 200:
        try:
            rates_data = response.json()
            exchange_rates = rates_data.get("rates", {})
            
            for currency in Currency.objects.all():
                exchange_rate = exchange_rates.get(currency.code)
                if exchange_rate is not None:
                    Currency.objects.filter(code=currency.code).update(rate=exchange_rate)
                else:
                    log.warning(f"Exchange rate for {currency.code} not found in the response.")
            
        except ValueError as e:
            log.warning(f"Error parsing JSON data: {e}")
        except Exception as e:
            log.warning(f"An error occurred: {e}")
            
        log.info(f'currency updated with openexchange API')
    else:
        log.warning(f"Error: {response.status_code} - Unable to fetch exchange rates.")
  
@shared_task      
def change_quotation_status():
    """
    This function changes the status of open quotations to 'expired' if their related quotationdata's valid_till date has passed.

    Returns:
        int: The number of quotations whose status was updated.
    """
    try:
        # Get open quotations that have not yet expired based on related quotationdata's valid_till
        expired_quotations = Quotation.objects.filter(status='open', quotation_data__valid_till__lte=timezone.now())      

        # Update the status for all expired quotations in a single query
        updated_count = expired_quotations.update(status='expired')
        
    except Exception as e:
        log.info(f"ERROR FOUND DURING STATUS CHANGE OF QTUOTATION: {e}")
        updated_count = 0
        
    log.info(f"Info: {updated_count} - Quotation Expired by celery.")
    return updated_count

@shared_task     
def send_quotation_reminder():
    """
    This function sends email notifications to the 'creator' of Quotation models
    before 5 days and 1 day of the 'valid_till' date.

    Returns:
        int: The number of email notifications sent.
    """
    # Get the current time
    current_time = timezone.now()

    # Calculate the target dates for sending emails (5 days and 1 day before 'valid_till')
    five_days_before = current_time + timezone.timedelta(days=5)
    one_day_before = current_time + timezone.timedelta(days=1)    
   
    quotations_to_notify = Quotation.objects.filter(status = 'open')

    from_email = settings.DEFAULT_FROM_EMAIL     
    email_messages = []  

    for quotation in quotations_to_notify:
      
        if hasattr(quotation, 'quotation_data') and hasattr(quotation, 'prices_of_quotation'):
            
            # Calculate the time difference between 'valid_till' and the target dates
            time_difference_5_days = quotation.quotationdata.valid_till - five_days_before
            time_difference_1_day = quotation.quotationdata.valid_till - one_day_before            

            # Check if the time difference is within a specific range (e.g., 24 hours)
            if 0 <= time_difference_5_days.total_seconds() <= 86400 or 0 <= time_difference_1_day.total_seconds() <= 86400:  # 86400 seconds = 24 hours
                # Customize the email content and subject as per your requirements
                subject = f"SINCEHHENCE LTD - Quotation Reminder of '{quotation.name}'"
                message = f"Dear {quotation.creator.username},\n\n" 
                message += f"Your quotation with number {quotation.quotation_data.quotation_number} is expiring on {quotation.quotation_data.valid_till}.\n\n" 
                message += f"Here is the link of it:\n\n"
                message += f"{build_full_url(quotation.get_absolute_url())}\n\n"
                message += f"Please click on the link to take necessary actions.\n\n"
                message += f"Best Regards\n\n"
                message += f"SinceHence Team\n\n"
                
                
                
                email_messages.append((subject, message, from_email, [quotation.creator.email] , '',  ['info@sincehence.co.uk'], ''))  
        else:        
            continue
        
    custom_send_mass_mail(email_messages, fail_silently=False)
    log.info(f"Info: {len(email_messages)} - Reminder mail sent by celery.")
    return len(email_messages)


   
@shared_task      
def sent_followup():
    try:       
        from_email = settings.DEFAULT_FROM_EMAIL    
        
        orders = Order.objects.filter(status__in=settings.INCOMPLETE_STATUS) \
            .exclude(total_followup__gte = 3) \
            .exclude(customer__isnull=True) \
   
        
        mail_sent = 0        
        
        for order in orders:
          
            if order.last_followup_on is not None:
                followup_on = order.last_followup_on
                cutoff_time = followup_on + timedelta(days=7)                 
            else:
                followup_on = timezone.now()
                cutoff_time = followup_on - timedelta(days=7)                 
                     
            # Check if there are no subsequent orders for this customer
            next_orders = Order.objects.filter(
                created_at__gt = order.created_at,                   
                customer = order.customer
            ).exclude(status__in = settings.INCOMPLETE_STATUS).exclude(status__in = settings.ABANDONED_STATUS)                 
        
            
            if not next_orders.exists():    
                if followup_on >= cutoff_time:            
                    subject = f"SINCEHHENCE LTD - Inclomplete Order Reminder for '{order.id}'!"
                    message = f"Dear {order.customer.username},\n\n"
                    message += f"You tried to make an order at our website. Somehow it may not have been processed. If you are still interested, you may choose any link from below:\n\n"             
                    if order.price.is_service:
                        message += f"<a href={build_full_url(reverse('shop:collect_requirements', args=[order.id, order.price.service.pk,  order.price.pk]))}>Start From Odrer Info</a>\n\n"                
                    if order.price.is_quotation:
                        message += f"<a href={build_full_url(reverse('shop:collect_requirements', args=[order.id, order.price.quotation.pk,  order.price.pk]))}>Start From Odrer Info</a>\n\n"
                    if order.gateway_payment_url:
                        message += f"<a href={order.gateway_payment_url}>Go to Payment Page Directly</a>\n\n"                    
                    
                    message += f"Looking forward to your actions.\n\n"
                    message += f"If you do not like to get this notification for this order, please delee the order from dasboard's abandoned order section.\n\n"
                    
                    message += f"Best Regards\n\n"
                    message += f"SinceHence Team\n\n"   
                 
                    custom_send_mail(subject, message, from_email, [order.customer.email], html_message=mark_safe(message))
                    mail_sent += 1
                    order.last_followup_on = timezone.now() + timedelta(days=1)  
                    order.total_followup += 1    
                    order.save()
            else:
                continue   
        # deleted = Order.objects.filter(status__in=settings.INCOMPLETE_STATUS, total_followup__gte = 3).delete()
        updated_count = Order.objects.filter(status__in=settings.INCOMPLETE_STATUS, total_followup__gte=3).update(status=settings.ABANDONED_STATUS)
        log.info(f"Info: {mail_sent} - folloup mail sent and {updated_count} marked as abadoned by celery.")
        return mail_sent, updated_count
    
    except Exception as e:   
        log.warning(f'importent: The problem found in cronjobs followup mail: {e}')
        return 0, 0
 
@shared_task        
def mark_abandoned_orders():
    try:
        # Get a list of order IDs to delete
        order_ids_to_delete = [
            invoice.order.id
            for invoice in OrderInvoice.objects.filter(due = True)
            if invoice.should_delete()
        ]

        # Bulk delete orders using their primary keys
        # total_deleted = Order.objects.filter(id__in=order_ids_to_delete).delete()
        updated_count = Order.objects.filter(id__in=order_ids_to_delete).update(status=settings.ABANDONED_STATUS)
        log.info(f"Info: {updated_count} - order abandoned by celery.")
        return updated_count  # Return the number of orders deleted
    except Exception as e:
        log.warning(f'Bulk delete failed due to error: {e}')
        return 0
     
    

        
        
# class RunSinceHenceCronJobs(CronJobBase):    
     
#     RUN_EVERY_MINS = 720  #per 12 hrs
#     RETRY_AFTER_FAILURE_MINS = 1
#     MIN_NUM_FAILURES = 2    
#     ALLOW_PARALLEL_RUNS = True
#     schedule = Schedule(run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
#     code = 'core.main_cron_job_12_hrs'   
    
#     def do(self):          
#         try:            
#             update_currency()
#             log.info(f'currency updated with openexchange API')
            
#             quotation_expired = change_quotation_status()
#             log.info(f"Info: {quotation_expired} - Quotation Expired by cronJOB.")
            
#             quotation_remainder = send_quotation_reminder()
#             log.info(f"Info: {quotation_remainder} - Reminder mail sent by cronJOB.")
            
#             mark_as_abandoned = mark_abandoned_orders()
#             log.info(f"Info: {mark_as_abandoned} - Due Order deleted by cronJOB.")
            
#             # abandoned = mark_abandoned()
#             # log.info(f"Info: {abandoned} - order abandoned by cronJOB.")
            
#             followup_sent, updated_count = sent_followup()
#             log.info(f"Info: {followup_sent} - folloup mail sent and {updated_count} marked as abadoned by cronJOB.")
#         except Exception as e:            
#             log.exception(f'An error occurred while running cronjob: {e}')
            
        
        
        
        
 