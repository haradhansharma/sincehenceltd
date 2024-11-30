from datetime import timedelta
from django.utils import timezone
import mimetypes
import os
import django
from django.http import HttpResponse
from django.urls import reverse
from reportlab.lib.pagesizes import letter, A3, A5, A4
from payment_method.gateways.bkash import bKashPaymentGateway
from payment_method.gateways.eximbd import EximBdPaymentGateway
from reportlab.lib.styles import ParagraphStyle   
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import black, red
from reportlab.pdfgen import canvas
from django.http import FileResponse
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.core.files import File
# from book.forms import PaymentForm
# from book.models import BookOrder, OrderInvoice
# from payment_method.forms import ConfirmForm
from payment_method.gateways.rocket import RocketPaymentGateway

from django.core.mail import EmailMessage, send_mail
from payment_method.tasks import send_email_task
from service.models import Order, OrderInvoice




def create_pdf_invoice(request, order, gateway):

    # Generate a unique filename for the PDF based on the order ID
    pdf_file_name = f'{order.id}.pdf'
    pdf_folder = settings.INVOICE_UPLOAD_TO
    
    uploaded_file_path = f'{pdf_folder}/{pdf_file_name}'
    
    # Create the directory if it doesn't exist
    pdf_dir = os.path.join(settings.MEDIA_ROOT, pdf_folder)
 
    
    
    # Define the criteria for getting or creating the record
    criteria = {
        'order': order,
        
    }

    # Try to get the existing record, or create a new one if it doesn't exist
    order_invoice_record, created = OrderInvoice.objects.get_or_create(
        defaults={
            'filepath': uploaded_file_path,
            'validity': timezone.now() + timezone.timedelta(days=settings.INVOICE_PAYMENT_VALIDITY_DAYS),
            'gateway': gateway.get_gateway_name(),
        },
        **criteria
    )
    
    # Create a PDF document and save it in the specified directory
    pdf_path = os.path.join(pdf_dir, pdf_file_name)
    
    # get file url to response            
    pdf_url = order_invoice_record.filepath.url              
    pagesize=A4
    #create PDF
    c = canvas.Canvas(pdf_path, pagesize=pagesize)
    
    page_width, page_height = pagesize    
    
    mergin = 2.54 * cm   
    
    c.setTitle(title = f'Order #{order.id} at {request.site.name}')
    c.setAuthor(f'{request.site.domain}')
    c.setCreator(f'{request.site.domain}')
    c.getPageNumber()            
    
    # Add content to the PDF
    c.setFont('Helvetica', 10)         
    
    c.beginText() 
    
    
    
    #styeles to be added
    left_style_black_head = ParagraphStyle(name="Times", fontName='Times-Roman', fontSize=10, leading=10, textColor= black, alignment=TA_CENTER)
    
    left_style_red_head = ParagraphStyle(name="Times", fontName='Times-Roman', fontSize=8, leading=10, textColor= red, alignment=TA_LEFT)
    left_style_red = ParagraphStyle(name="Times", fontName='Times-Roman', fontSize=8, leading=10, textColor= red, alignment=TA_LEFT)
    left_style_black = ParagraphStyle(name="Times", fontName='Times-Roman', fontSize=7, leading=10, textColor= black, alignment=TA_LEFT)
    
    # Define your company header content
    company_header_content = """
    <b>Sankarmath - o - Mission</b><br/>
    www.sankarmath.org, www.sankarmath-o-mission.org<br/>
    Email: info@sankarmath.org<br/>

    """
    
    aW = page_width - mergin * 2 
    aH = page_height  
    status = 'PAID' if order.pending_amount <= 0 else 'UNPAID'      
    data = [   
            ('left_style_black_head' , f'{company_header_content}'),  
            ('left_style_black' , f' <br/> <br/> '),    
            ('left_style_red_head' , f'ORDER #{order.order_number}'),    
            ('left_style_red' , f'{order.price}'),
            ('left_style_black' , f' <br/> <br/> '),    
            ('left_style_black' , f'Payment Instruction:'), 
            ('left_style_black' , f' <br/> '),   
            ('left_style_black' , f'Pay To: {gateway.get_pay_to()}'),  
            ('left_style_black' , f'Amount: {order.amount} BDT'), 
            ('left_style_black' , f'Due: {order.pending_amount} BDT'),  
            ('left_style_black' , f' <br/> <br/>'),      
            ('left_style_black' , f'Invoice Status: {status}'),  
            ('left_style_black' , f'Order Status: {order.status.upper()}'),              
            ('left_style_black' , f' <br/> <br/> '),                
            ('left_style_black' , f'Pay Through: {gateway.get_help_text()}'),     
            ('left_style_black' , f'Account Number: {gateway.get_account()}'),   
            ('left_style_black' , f'Due Date: {order_invoice_record.validity.date()}'),  
            ('left_style_black' , f' <br/> <br/>  '),  
            ('left_style_red' , f'<i>Please pay before the validity.</i>'),                 
        ]  
        
    


  
 
    
    for style, values in data:        
        p = Paragraph(values, locals()[style])        
        w,h = p.wrap(aW, aH) # find required space    
        aH -= h  # reduce the available height starting from first line  
        if w <= aW and h <= aH:
            p.drawOn(c,mergin,aH)
            aH = aH #protect to be double line          
        else:
            aH = aH
            c.showPage()            
            # raise ValueError('Not enogugh room')
            w,h = p.wrap(aW, aH) # find required space        
            if w <= aW and h <= aH:
                p.drawOn(c,mergin,aH)
                aH -= h # reduce the available height   
            continue   
    
    # Close the PDF document
    c.save()
    
    # Send an email to the user
    subject = 'SinceHence Ltd | Invoice Update!'
    message =   f'Hello {order.customer.email},\n\n'
    message +=  f'An update of your order: \n\n' 
    message +=  f'Order number is: #{order.order_number}. \n' 
    message +=  f'Order amount is: {order.amount}. \n' 
    message +=  f'Order Due: {order.pending_amount}. Due date: {order.invoice.validity.date()} \n' 
    message +=  f'Order Status: {order.status}.\n\n'     
    
    message +=  f'Here we are attaching the invoice generated against the order.\n\n'                     
    message +=  f'Please follow the link to update payment information after paying the order amount acording to the details mentioned in the invoice.\n\n' 
    message +=  f'Best Regards...\n\n' 
    message +=  f'SinceHence Ltd\n\n' 

    from_email = settings.DEFAULT_FROM_EMAIL     
    recipient_list = [order.customer.email]
    send_email_task.delay(subject, message, from_email, recipient_list, pdf_path)
    # email = EmailMessage(subject, message, from_email, recipient_list)
    # email.attach_file(pdf_path)  

    # # Send the email
    # email.send()
    
    # Return the PDF file
    response = FileResponse(pdf_path, content_type='application/pdf')
    
    return pdf_url, response





def bkash_manual(request, order_id):
    order = get_object_or_404(Order, id = order_id)
    
    gateway = bKashPaymentGateway()
    gatway_instruction = gateway.get_gateway_instruction(order)

    template = 'service/success.html'
    
    order.status = 'invoice_initiatd'
    order.save()
   
    pdf_url, response = create_pdf_invoice(request, order, gateway)
    
    if response.status_code == 200:  
        pending_payment_order = order.invoice.update_payment_url
        html_content = f'<h5>Payment Instruction:</h5>' 
        html_content += f'<p class="text-primary fs-6">Below is the invoice for your order.</p>'  
        html_content += f'<p class="text-primary fs-6">After payment please update your payment information there. It has to be done. Otherwise there is no way to get updated.</p>'  
        html_content += f'<p class="text-primary fs-6">If you paid already, click the button to update:  <a class="btn btn-default" href="{pending_payment_order}">Update #{order.id}</a></p>'   
        html_content += f'<p class="text-primary fs-6">So that we can start processing this order.</p>'                 
                        
                        
        html_content += f'<iframe src="{pdf_url}" width="100%" height="500"></iframe>'  
        # return HttpResponse(html_content)
    else:
        html_content = 'There is system error in creaing invoice!'
    payment_status = 'PAID' if order.pending_amount <= 0 else 'UNPAID'   
    context = {
                'order' : order,       
                'html_content' : html_content,
                'gatway_instruction' : gatway_instruction,
                'payment_status' : payment_status
                
            }
    return render(request, template, context)
    
 
    
    # if request.method == 'POST':  
    #     payment_form = ConfirmForm(request.POST, request.FILES)
    #     if payment_form.is_valid():
    #         order.order_status = 'invoice_initiatd'
    #         order.save()
            
    #         pdf_url, response = create_pdf_invoice(request, order, gateway)
            
            
            
    #         if response.status_code == 200: 
    #             panding_payment_url = reverse('accounts:pending_payments')
    #             pending_payment_order = reverse('accounts:pending_payments') + f'?search={order.id}'
    #             html_content = f'<h5>Payment Instruction:</h5>' 
    #             html_content += f'<p class="text-primary fs-6">Below is the invoice for your order. It can be found by clicking "<a href={panding_payment_url}>Pending Payment</a>" button from the site footer as well.</p>'  
    #             html_content += f'<p class="text-primary fs-6">After payment please update your payment information there. It has to be done. Otherwise there is no way to get updated.</p>'  
    #             html_content += f'<p class="text-primary fs-6">If you paid already, click the button to update:  <a class="btn btn-default" href="{pending_payment_order}">Update #{order.id}</a></p>'   
    #             html_content += f'<p class="text-primary fs-6">So that we can start processing this order.</p>'                 
                              
                               
    #             html_content += f'<iframe src="{pdf_url}" width="100%" height="500"></iframe>'  
    #             return HttpResponse(html_content)
    #     else:
    #         context = {
    #             'order' : order,       
    #             'payment_form' : payment_form,
    #             'gatway_instruction' : gatway_instruction
                
    #         }
    #         return render(request, template, context)
        
    # context = {
    #     'order' : order, 
    #     'payment_form' : payment_form,
    #     'gatway_instruction' : gatway_instruction
        
    # }

    
    # return render(request, template, context)

def exim_bd(request, order_id):     
    order = get_object_or_404(BookOrder, id = order_id)
    
    gateway = EximBdPaymentGateway()
    gatway_instruction = gateway.get_gateway_instruction(order)
    print(gateway)
    template = 'payment_method/eximbd.html'    
    
    payment_form = ConfirmForm()
    
    if request.method == 'POST':  
        payment_form = ConfirmForm(request.POST, request.FILES)
        if payment_form.is_valid():    
            
            order.order_status = 'invoice_initiatd'
            order.save()        

            pdf_url, response = create_pdf_invoice(request, order, gateway)
            
            
            
            
            if response.status_code == 200: 
                panding_payment_url = reverse('accounts:pending_payments')
                pending_payment_order = reverse('accounts:pending_payments') + f'?search={order.id}'
                html_content = f'<h5>Payment Instruction:</h5>' 
                html_content += f'<p class="text-primary fs-6">Below is the invoice for your order. It can be found by clicking "<a href={panding_payment_url}>Pending Payment</a>" button from the site footer as well.</p>'  
                html_content += f'<p class="text-primary fs-6">After payment please update your payment information there. It has to be done. Otherwise there is no way to get updated.</p>'  
                html_content += f'<p class="text-primary fs-6">If you paid already, click the button to update:  <a class="btn btn-default" href="{pending_payment_order}">Update #{order.id}</a></p>'   
                html_content += f'<p class="text-primary fs-6">So that we can start processing this order.</p>'                 
                              
                               
                html_content += f'<iframe src="{pdf_url}" width="100%" height="500"></iframe>'  
                return HttpResponse(html_content)
            

        else:
            context = {
                'order' : order,       
                'payment_form' : payment_form,
                'gatway_instruction' : gatway_instruction
                
            }
            return render(request, template, context)
        
    context = {
        'order' : order, 
        'payment_form' : payment_form,
        'gatway_instruction' : gatway_instruction
        
    }

    
    return render(request, template, context)


def rocket_manual(request, order_id):    
    order = get_object_or_404(BookOrder, id = order_id)
    
    gateway = RocketPaymentGateway()
    gatway_instruction = gateway.get_gateway_instruction(order)
    
    template = 'payment_method/rocket_manual.html'
    
    payment_form = ConfirmForm()
    
    if request.method == 'POST':  
        payment_form = ConfirmForm(request.POST, request.FILES)
        if payment_form.is_valid():
            order.order_status = 'invoice_initiatd'
            order.save()
            
            pdf_url, response = create_pdf_invoice(request, order, gateway)
            
            
            
            if response.status_code == 200: 
                panding_payment_url = reverse('accounts:pending_payments')
                pending_payment_order = reverse('accounts:pending_payments') + f'?search={order.id}'
                html_content = f'<h5>Payment Instruction:</h5>' 
                html_content += f'<p class="text-primary fs-6">Below is the invoice for your order. It can be found by clicking "<a href={panding_payment_url}>Pending Payment</a>" button from the site footer as well.</p>'  
                html_content += f'<p class="text-primary fs-6">After payment please update your payment information there. It has to be done. Otherwise there is no way to get updated.</p>'  
                html_content += f'<p class="text-primary fs-6">If you paid already, click the button to update:  <a class="btn btn-default" href="{pending_payment_order}">Update #{order.id}</a></p>'   
                html_content += f'<p class="text-primary fs-6">So that we can start processing this order.</p>'                 
                              
                               
                html_content += f'<iframe src="{pdf_url}" width="100%" height="500"></iframe>'  
                return HttpResponse(html_content)
        else:
            context = {
                'order' : order,       
                'payment_form' : payment_form,
                'gatway_instruction' : gatway_instruction
                
            }
            return render(request, template, context)
        
    context = {
        'order' : order, 
        'payment_form' : payment_form,
        'gatway_instruction' : gatway_instruction
        
    }

    
    return render(request, template, context) 