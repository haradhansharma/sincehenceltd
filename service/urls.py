
from django.urls import path, include
from .views import *

app_name = 'service'

urlpatterns = [
    path('', ServiceList.as_view(), name='service_list'),
    path('<uuid:pk>/', ServiceDetailView.as_view(), name='service_details'),
    # path('collect-requirements/<uuid:order_id>/<uuid:pk1>/<uuid:pk2>/', CollectRequirements.as_view(), name='collect_requirements'),
    path('collect-order-info/<uuid:service_id>/<uuid:selected_price_id>/', CollectOrderInfo.as_view(), name='collect_order_info'),
    
    path('quotation-request/<uuid:pk>/', QuotationRequest.as_view(), name="quotation_request"),
    path('web-quotation/<uuid:pk>/', QuotationDetail.as_view(), name="web_quotation"),
    path('pdf-quotation/<uuid:pk>/', QuotationPDF.as_view(), name="pdf_quotation"),
    path('payment-success/', payment_success, name="payment_success"),
    path('payment-cancel/', payment_cancel, name="payment_cancel"),  
    path('update-payment/<uuid:id>', update_payment, name='update_payment'),  
    path('cancel-order/<uuid:id>', cancel_order, name='cancel_order'),  
    
    
    
]
