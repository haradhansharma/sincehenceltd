# Generated by Django 4.2.2 on 2023-11-14 06:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0003_servicecategory_banner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='categories',
        ),
    ]
