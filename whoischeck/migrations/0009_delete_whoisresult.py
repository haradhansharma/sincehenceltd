# Generated by Django 4.2.2 on 2024-06-09 07:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('whoischeck', '0008_alter_whoisresult_domain_name'),
    ]

    operations = [
        migrations.DeleteModel(
            name='WhoisResult',
        ),
    ]
