from django.urls import path
from . import views
app_name = 'sourcing' 
urlpatterns = [
    # Supplier Profile URLs
    path('supplier/add/', views.add_supplier, name='add_supplier'),
    path('supplier/<int:supplier_id>/', views.view_supplier, name='view_supplier'),
    path('supplier/<int:supplier_id>/edit/', views.edit_supplier, name='edit_supplier'),
    path('supplier/<int:supplier_id>/delete/', views.delete_supplier, name='delete_supplier'),
    path('suppliers/', views.list_suppliers, name='list_suppliers'),

    # Product Link URLs
    path('product/add/<int:supplier_id>/', views.add_product_link, name='add_product_link'),
    path('product/<int:product_link_id>/edit/', views.edit_product_link, name='edit_product_link'),
    path('product/<int:product_link_id>/delete/', views.delete_product_link, name='delete_product_link'),
    path('products/', views.list_product_links, name='list_product_links'),
    


    # Discussion Record URLs
    path('discussion/<int:supplier_id>/<int:product_link_id>/add/', views.add_discussion_record, name='add_discussion_record'),
    path('discussion/<int:discussion_record_id>/edit/', views.edit_discussion_record, name='edit_discussion_record'),
    path('discussion/<int:discussion_record_id>/delete/', views.delete_discussion_record, name='delete_discussion_record'),

    # Sourcing Progress URLs
    path('progress/<int:product_link_id>/edit/', views.edit_sourcing_progress, name='edit_sourcing_progress'),

    # Proforma Invoice URLs    
    path('invoice/<int:supplier_id>/<int:product_link_id>/add/', views.add_proforma_invoice, name='add_proforma_invoice'),
    path('invoice/<int:proforma_invoice_id>/edit/', views.edit_proforma_invoice, name='edit_proforma_invoice'),
    path('invoice/<int:proforma_invoice_id>/delete/', views.delete_proforma_invoice, name='delete_proforma_invoice'),

    # Order URLs
    path('piorder/<int:supplier_id>/<int:product_link_id>/<int:pi_id>/add/', views.add_order, name='add_order'),
    path('piorder/<int:order_id>/edit/', views.edit_order, name='edit_order'),
    path('piorder/<int:order_id>/delete/', views.delete_order, name='delete_order'),


    # Shipping Record URLs   
    path('shipping/<int:supplier_id>/<int:product_link_id>/<int:pi_id>/<int:pi_order_id>/add/', views.add_osr, name='add_osr'),
    path('shipping/<int:osr_id>/edit/', views.edit_osr, name='edit_osr'),
    path('shipping/<int:osr_id>/delete/', views.delete_osr, name='delete_osr'),
    
]
