# Generated by Django 4.2.2 on 2024-01-12 00:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0075_interactions'),
    ]

    operations = [
        migrations.AddField(
            model_name='interactions',
            name='reply_accepted',
            field=models.BooleanField(default=False),
        ),
    ]
