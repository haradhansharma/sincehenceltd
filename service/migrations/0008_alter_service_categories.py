# Generated by Django 4.2.2 on 2023-11-14 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0007_remove_service_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='categories',
            field=models.ManyToManyField(related_name='category_services', to='service.servicecategory'),
        ),
    ]
