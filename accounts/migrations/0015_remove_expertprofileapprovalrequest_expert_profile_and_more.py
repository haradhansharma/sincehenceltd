# Generated by Django 4.2.2 on 2024-01-03 21:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_expertprofileapprovalrequest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expertprofileapprovalrequest',
            name='expert_profile',
        ),
        migrations.RemoveField(
            model_name='expertprofileapprovalrequest',
            name='status',
        ),
        migrations.DeleteModel(
            name='ExpertiesProfile',
        ),
        migrations.DeleteModel(
            name='ExpertProfileApprovalRequest',
        ),
    ]
