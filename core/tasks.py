from celery import shared_task
from core.helper import custom_send_mail, custom_send_mass_mail


import logging
log =  logging.getLogger('log')


@shared_task
def send_mass_mail_task(datatuple, fail_silently=False, auth_user=None, auth_password=None, connection=None):
    try:
        custom_send_mass_mail(
            datatuple, fail_silently=fail_silently, auth_user=auth_user, auth_password=auth_password, connection=connection
        )
        log.info(f"mass mail sent")
    except Exception as e:
        log.error(f"Failed to send mass mail due to: {e}")
        
@shared_task
def custom_send_mail_task(
    subject,
    message,
    from_email,
    recipient_list,
    fail_silently=False,
    auth_user=None,
    auth_password=None,
    connection=None,
    html_message=None,
    cc=None,
    reply_to=None,
    bcc=None
    ):
    try:
        custom_send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=fail_silently,
            auth_user=auth_user,
            auth_password=auth_password,
            connection=connection,
            html_message=html_message,
            cc=cc,
            reply_to=reply_to,
            bcc=bcc,
        )
        log.info(f"mail sent")
    except Exception as e:
        log.error(f"Failed to send  mail due to: {e}")
        
        

        
            