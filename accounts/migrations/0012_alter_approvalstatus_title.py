# Generated by Django 4.2.2 on 2024-01-02 22:33

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_approvalstatus_expertiesprofile_skill_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approvalstatus',
            name='title',
            field=models.CharField(max_length=150, unique=True, validators=[django.core.validators.RegexValidator(flags=re.RegexFlag['IGNORECASE'], message="Title must be 'approved', 'rejected', or 'pending', optionally followed by a hyphen and additional words.", regex='^(approved|rejected|pending)(?:-[\\w-]*)?$')]),
        ),
    ]
