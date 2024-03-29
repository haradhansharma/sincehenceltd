# Generated by Django 4.2.2 on 2023-11-07 00:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link_title', models.CharField(blank=True, max_length=252, null=True)),
                ('product_type', models.CharField(blank=True, max_length=252, null=True)),
                ('url', models.URLField(unique=True)),
                ('link_img_url', models.URLField(blank=True, null=True)),
                ('importance', models.IntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])),
                ('notes', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ProformaInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('attachments', models.FileField(blank=True, null=True, upload_to='sourcing/proforma_invoices/')),
                ('product_link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sourcing.productlink')),
            ],
        ),
        migrations.CreateModel(
            name='SupplierProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('company', models.CharField(max_length=100)),
                ('contact_information', models.TextField(blank=True, null=True)),
                ('website', models.URLField(unique=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SourcingProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('progress_status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')], max_length=100)),
                ('progress_notes', models.TextField()),
                ('product_link', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='sourcing.productlink')),
            ],
        ),
        migrations.CreateModel(
            name='SourcingOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('proforma_invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sourcing.proformainvoice')),
            ],
        ),
        migrations.AddField(
            model_name='productlink',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sourcing.supplierprofile'),
        ),
        migrations.CreateModel(
            name='OrderShippingRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shipping_date', models.DateField()),
                ('shipping_details', models.TextField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sourcing.sourcingorder')),
            ],
        ),
        migrations.CreateModel(
            name='DiscussionRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('discussion_details', models.TextField()),
                ('product_link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sourcing.productlink')),
            ],
        ),
    ]
