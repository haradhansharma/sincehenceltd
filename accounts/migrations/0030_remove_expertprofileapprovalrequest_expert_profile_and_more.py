# Generated by Django 4.2.2 on 2024-01-09 02:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0058_remove_projectcontributor_contributor'),
        ('accounts', '0029_alter_expertiesprofile_id_and_more'),
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
