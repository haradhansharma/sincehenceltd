# Generated by Django 4.2.2 on 2023-12-25 03:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shcurrency', '0001_initial'),
        ('service', '0015_order_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_currency', to='shcurrency.currency'),
        ),
    ]
