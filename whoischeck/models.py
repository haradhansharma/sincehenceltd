from django.db import models

from core.mixins import DateFieldModelMixin

class WhoisResult(
    DateFieldModelMixin,
    models.Model
    ):
    domain_name = models.CharField(max_length=255, help_text = "Write without http or https. example: ebay.com, amazon.com, google.com.bd etc")
    registrar = models.TextField(blank=True, null=True)
    registrant_name = models.CharField(max_length=255, blank=True, null=True)
    registrant_organization = models.CharField(max_length=255, blank=True, null=True)
    name_server = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)
    expiration_date = models.DateTimeField(blank=True, null=True)
