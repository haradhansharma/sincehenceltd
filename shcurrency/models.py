from django.db import models

# Create your models here.
class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=5)
    rate = models.DecimalField(decimal_places=10, max_digits=15)
   
 

    def __str__(self):
        return self.code