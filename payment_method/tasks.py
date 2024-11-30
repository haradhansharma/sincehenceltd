from celery import shared_task
from django.core.mail import EmailMessage
import logging

from core.helper import custom_send_mass_mail
log =  logging.getLogger('log')


@shared_task
def send_email_task(subject, message, from_email, recipient_list, pdf_path=None):
    try:
        email = EmailMessage(subject, message, from_email, recipient_list)
        if pdf_path:
            email.attach_file(pdf_path)
        email.send()
        log.info(f"Email successfully sent to {', '.join(recipient_list)}")
        return f"Email sent to {', '.join(recipient_list)}"
    except Exception as e:
        log.error(f"Failed to send email to {', '.join(recipient_list)}: {str(e)}")
        
    

        