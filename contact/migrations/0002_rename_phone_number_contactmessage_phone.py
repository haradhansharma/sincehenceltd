# Generated by Django 4.2.2 on 2023-11-17 16:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contactmessage',
            old_name='phone_number',
            new_name='phone',
        ),
    ]
