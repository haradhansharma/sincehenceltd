# Generated by Django 4.2.2 on 2024-01-01 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendar_app', '0004_alter_weekendday_day_of_week'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weekendday',
            name='day_of_week',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Sunday'), (1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday')]),
        ),
    ]
