# Generated by Django 4.2.2 on 2023-12-31 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendar_app', '0002_alter_weekendday_day_of_week'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weekendday',
            name='day_of_week',
            field=models.CharField(choices=[('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')], max_length=1),
        ),
    ]
