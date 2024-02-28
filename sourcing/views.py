from django.shortcuts import render, redirect, get_object_or_404
from .models import DiscussionRecord, OrderShippingRecord, ProductLink, ProformaInvoice, SourcingOrder, SourcingProgress, SupplierProfile
from .forms import DiscussionRecordForm, OrderShippingRecordForm, ProductLinkForm, ProformaInvoiceForm, SourcingOrderForm, SourcingProgressForm, SupplierForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

def get_paginated_items(request, model):    
    items = model.objects.all().order_by('-id')
    paginator = Paginator(items, 10) 
    page_number = request.GET.get('page')
    
    try:
        items = paginator.page(page_number)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)   
        
    return  items


def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.user = request.user
            supplier.save()

            suppliers = get_paginated_items(request, SupplierProfile)
            return render(request, 'sourcing/list_suppliers_hx.html', {'suppliers': suppliers})
    else:
        form = SupplierForm()
    return render(request, 'sourcing/add_supplier.html', {'form': form})

def edit_supplier(request, supplier_id):
    supplier = get_object_or_404(SupplierProfile, pk=supplier_id)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            suppliers = get_paginated_items(request, SupplierProfile)
            return render(request, 'sourcing/list_suppliers_hx.html', {'suppliers': suppliers})
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'sourcing/edit_supplier.html', {'form': form, 'supplier': supplier})

def delete_supplier(request, supplier_id):
    supplier = get_object_or_404(SupplierProfile, pk=supplier_id)
    if request.method == 'POST':
        supplier.delete()
        suppliers = get_paginated_items(request, SupplierProfile)
        return render(request, 'sourcing/list_suppliers_hx.html', {'suppliers': suppliers})
    return render(request, 'sourcing/delete_supplier.html', {'supplier': supplier})

def view_supplier(request, supplier_id):
    supplier = get_object_or_404(SupplierProfile, pk=supplier_id)
    return render(request, 'sourcing/view_supplier.html', {'supplier': supplier})

def list_suppliers(request):
    suppliers = get_paginated_items(request, SupplierProfile)
    return render(request, 'sourcing/list_suppliers.html', {'suppliers': suppliers})

def list_product_links(request):
    product_links = get_paginated_items(request, ProductLink)
    return render(request, 'sourcing/list_product_links.html', {'product_links': product_links})

def add_product_link(request, supplier_id):
    supplier = get_object_or_404(SupplierProfile, pk=supplier_id)

    if request.method == 'POST':
        form = ProductLinkForm(request.POST)
        if form.is_valid():
            product_link = form.save(commit=False)
            product_link.supplier = supplier
            product_link.save()
            return redirect('sourcing:view_supplier', supplier_id=supplier.id)
    else:
        form = ProductLinkForm()

    return render(request, 'sourcing/add_product_link.html', {'form': form, 'supplier': supplier})



def edit_product_link(request, product_link_id):
    product_link = get_object_or_404(ProductLink, pk=product_link_id)
  
    if request.method == 'POST':        
        form = ProductLinkForm(request.POST, instance=product_link)
        if form.is_valid():
            form.save()
            return redirect('sourcing:view_supplier', supplier_id=product_link.supplier.id)
    else:
        form = ProductLinkForm(instance=product_link)

    return render(request, 'sourcing/edit_product_link.html', {'form': form, 'product_link': product_link})


def delete_product_link(request, product_link_id):
    product_link = get_object_or_404(ProductLink, pk=product_link_id)
    supplier_id = product_link.supplier.id

    if request.method == 'POST':
        product_link.delete()
        return redirect('sourcing:view_supplier', supplier_id=supplier_id)

    return render(request, 'sourcing/delete_product_link.html', {'product_link': product_link})


def add_discussion_record(request, supplier_id, product_link_id):
    product_link = get_object_or_404(ProductLink, pk=product_link_id)
    if request.method == 'POST':
        form = DiscussionRecordForm(request.POST)
        if form.is_valid():
            discussion_record = form.save(commit=False)
            discussion_record.product_link = product_link
            discussion_record.save()
            return redirect('sourcing:view_supplier', supplier_id=supplier_id)
    else:
        form = DiscussionRecordForm()

    return render(request, 'sourcing/add_discussion_record.html', {'form': form, 'product_link': product_link})

def edit_discussion_record(request, discussion_record_id):
    discussion_record = get_object_or_404(DiscussionRecord, pk=discussion_record_id)

    if request.method == 'POST':
        form = DiscussionRecordForm(request.POST, instance=discussion_record)
        if form.is_valid():
            form.save()
            return redirect('sourcing:view_supplier', supplier_id=discussion_record.product_link.supplier.id)
    else:
        form = DiscussionRecordForm(instance=discussion_record)

    return render(request, 'sourcing/edit_discussion_record.html', {'form': form, 'discussion_record': discussion_record})

def delete_discussion_record(request, discussion_record_id):
    discussion_record = get_object_or_404(DiscussionRecord, pk=discussion_record_id)
    supplier_id = discussion_record.product_link.supplier.id

    if request.method == 'POST':
        discussion_record.delete()
        return redirect('sourcing:view_supplier', supplier_id=supplier_id)

    return render(request, 'sourcing/delete_discussion_record.html', {'discussion_record': discussion_record})



def edit_sourcing_progress(request, product_link_id):
    product_link = get_object_or_404(ProductLink, pk=product_link_id)
    sourcing_progress, created = SourcingProgress.objects.get_or_create(product_link=product_link)

    if request.method == 'POST':
        form = SourcingProgressForm(request.POST, instance=sourcing_progress)
        if form.is_valid():
            form.save()
            return redirect('sourcing:view_supplier', supplier_id=product_link.supplier.id)
    else:
        form = SourcingProgressForm(instance=sourcing_progress)

    return render(request, 'sourcing/edit_sourcing_progress.html', {'form': form, 'product_link': product_link})


def add_proforma_invoice(request, supplier_id, product_link_id):
    product_link = get_object_or_404(ProductLink, pk=product_link_id)
    if request.method == 'POST':
        form = ProformaInvoiceForm(request.POST, request.FILES)
        if form.is_valid():
            proforma_invoice = form.save(commit=False)
            proforma_invoice.product_link = product_link
            proforma_invoice.save()
            return redirect('sourcing:view_supplier', supplier_id=supplier_id)
        else:
            print(form.errors)
    else:
        form = ProformaInvoiceForm()

    return render(request, 'sourcing/add_proforma_invoice.html', {'form': form, 'product_link': product_link})

def edit_proforma_invoice(request, proforma_invoice_id):
    proforma_invoice = get_object_or_404(ProformaInvoice, pk=proforma_invoice_id)

    if request.method == 'POST':
        form = ProformaInvoiceForm(request.POST, request.FILES, instance=proforma_invoice)
        if form.is_valid():
            form.save()
            return redirect('sourcing:view_supplier', supplier_id=proforma_invoice.product_link.supplier.id)
    else:
        form = ProformaInvoiceForm(instance=proforma_invoice)

    return render(request, 'sourcing/edit_proforma_invoice.html', {'form': form, 'proforma_invoice': proforma_invoice})

def delete_proforma_invoice(request, proforma_invoice_id):
    proforma_invoice = get_object_or_404(ProformaInvoice, pk=proforma_invoice_id)
    supplier_id = proforma_invoice.product_link.supplier.id

    if request.method == 'POST':
        proforma_invoice.delete()
        return redirect('sourcing:view_supplier', supplier_id=supplier_id)

    return render(request, 'sourcing/delete_proforma_invoice.html', {'proforma_invoice': proforma_invoice})


def add_order(request, supplier_id, product_link_id, pi_id):
    proforma_invoice = get_object_or_404(ProformaInvoice, pk=pi_id)
    if request.method == 'POST':
        form = SourcingOrderForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            order.proforma_invoice = proforma_invoice
            order.save()
            return redirect('sourcing:view_supplier', supplier_id=supplier_id)
        
    else:
        form = SourcingOrderForm()

    return render(request, 'sourcing/add_order.html', {'form': form, 'proforma_invoice': proforma_invoice})

def edit_order(request, order_id):
    order = get_object_or_404(SourcingOrder, pk=order_id)

    if request.method == 'POST':
        form = SourcingOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('sourcing:view_supplier', supplier_id=order.proforma_invoice.product_link.supplier.id)
    else:
        form = SourcingOrderForm(instance=order)

    return render(request, 'sourcing/edit_order.html', {'form': form, 'order': order})

def delete_order(request, order_id):
    order = get_object_or_404(SourcingOrder, pk=order_id)
    supplier_id = order.proforma_invoice.product_link.supplier.id

    if request.method == 'POST':
        order.delete()
        return redirect('sourcing:view_supplier', supplier_id=supplier_id)

    return render(request, 'sourcing/delete_order.html', {'order': order})


def add_osr(request, supplier_id, product_link_id, pi_id, pi_order_id):
    sourcing_order = get_object_or_404(SourcingOrder, pk=pi_order_id)
    if request.method == 'POST':
        form = OrderShippingRecordForm(request.POST, request.FILES)
        if form.is_valid():
            osr = form.save(commit=False)
            osr.order = sourcing_order
            osr.save()
            return redirect('sourcing:view_supplier', supplier_id=supplier_id)        
    else:
        form = OrderShippingRecordForm()

    return render(request, 'sourcing/add_osr.html', {'form': form, 'sourcing_order': sourcing_order})

def edit_osr(request, osr_id):
    osr = get_object_or_404(OrderShippingRecord, pk=osr_id)

    if request.method == 'POST':
        form = OrderShippingRecordForm(request.POST, instance=osr)
        if form.is_valid():
            form.save()
            return redirect('sourcing:view_supplier', supplier_id=osr.order.proforma_invoice.product_link.supplier.id)
    else:
        form = OrderShippingRecordForm(instance=osr)

    return render(request, 'sourcing/edit_osr.html', {'form': form, 'osr': osr})

def delete_osr(request, osr_id):
    osr = get_object_or_404(OrderShippingRecord, pk=osr_id)
    supplier_id = osr.order.proforma_invoice.product_link.supplier.id

    if request.method == 'POST':
        osr.delete()
        return redirect('sourcing:view_supplier', supplier_id=supplier_id)

    return render(request, 'sourcing/delete_osr.html', {'osr': osr})

