# Generated by Django 4.2.2 on 2024-01-07 11:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0024_rename_remarks_verificationfiles_office_remarks_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='verificationfiles',
            name='status',
        ),
        migrations.RemoveField(
            model_name='verificationfiles',
            name='v_request',
        ),
        migrations.DeleteModel(
            name='UserVerificationRequest',
        ),
        migrations.DeleteModel(
            name='VerificationFiles',
        ),
    ]
