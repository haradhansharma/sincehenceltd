# Generated by Django 4.2.2 on 2024-01-02 22:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_alter_approvalstatus_title'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ExpertProfileApprovalRequest',
        ),
    ]
