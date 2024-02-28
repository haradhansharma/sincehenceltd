from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.
class ContactMessage(models.Model):   
    name = models.CharField(max_length=255)
    phone = PhoneNumberField()
    email = models.EmailField()
    subject = models.CharField(max_length=251)  
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.email})'