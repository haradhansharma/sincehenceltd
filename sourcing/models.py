from django.db import models
from accounts.models import User

class SupplierProfile(models.Model):
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    contact_information = models.TextField(null=True, blank=True)
    website = models.URLField(unique=True)
    notes = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    @property
    def has_product_link(self):
        return self.productlink_set.exists()

    def __str__(self):
        return self.name

class ProductLink(models.Model):
    link_title = models.CharField(max_length=252, null=True, blank=True)
    product_type = models.CharField(max_length=252, null=True, blank=True)    
    url = models.URLField(unique=True)
    link_img_url = models.URLField(null=True, blank=True)
    supplier = models.ForeignKey(SupplierProfile, on_delete=models.CASCADE)
    importance = models.IntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])
    notes = models.CharField(max_length=100)

    def __str__(self):
        return self.url
    
    @property
    def has_discussion_records(self):
        return self.discussionrecord_set.exists()
    
    @property
    def has_performa_invoices(self):
        return self.proformainvoice_set.exists()

class DiscussionRecord(models.Model):
    product_link = models.ForeignKey(ProductLink, on_delete=models.CASCADE)
    date = models.DateField()
    discussion_details = models.TextField()

class SourcingProgress(models.Model):
    product_link = models.OneToOneField(ProductLink, on_delete=models.CASCADE)
    progress_status = models.CharField(max_length=100, choices=[('pending', 'Pending'),('in_progress', 'In Progress'), ('completed', 'Completed')])
    progress_notes = models.TextField()

class ProformaInvoice(models.Model):
    product_link = models.ForeignKey(ProductLink, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=100)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    attachments = models.FileField(upload_to='sourcing/proforma_invoices/', null=True, blank=True)
    
    @property
    def has_sourcing_orders(self):
        return self.sourcingorder_set.exists()

class SourcingOrder(models.Model):
    proforma_invoice = models.ForeignKey(ProformaInvoice, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=100)
    date = models.DateField()
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def has_osr(self):
        return self.ordershippingrecord_set.exists()

class OrderShippingRecord(models.Model):
    order = models.ForeignKey(SourcingOrder, on_delete=models.CASCADE)
    shipping_date = models.DateField()
    shipping_details = models.TextField()

    def __str__(self):
        return f"Shipping on {self.shipping_date}"
