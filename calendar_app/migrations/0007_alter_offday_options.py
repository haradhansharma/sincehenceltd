# Generated by Django 4.2.2 on 2024-01-01 21:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calendar_app', '0006_rename_date_offday_selected_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='offday',
            options={'ordering': ('selected_date',)},
        ),
    ]
