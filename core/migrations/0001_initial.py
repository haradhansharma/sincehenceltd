# Generated by Django 4.2.2 on 2023-11-07 00:24

import django.contrib.sites.managers
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExSite',
            fields=[
                ('site', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='sites.site', verbose_name='site')),
                ('site_description', models.TextField(max_length=500)),
                ('site_meta_tag', models.CharField(max_length=255)),
                ('site_favicon', models.ImageField(upload_to='site_image/')),
                ('site_logo', models.ImageField(upload_to='site_image/')),
                ('trademark', models.ImageField(upload_to='site_image/')),
                ('slogan', models.CharField(default='', max_length=150)),
                ('og_image', models.ImageField(upload_to='site_image/')),
                ('mask_icon', models.FileField(upload_to='site_image/', validators=[django.core.validators.FileExtensionValidator(['svg'])])),
                ('facebook_link', models.URLField()),
                ('twitter_link', models.URLField()),
                ('linkedin_link', models.URLField()),
                ('instagram_link', models.URLField()),
                ('email', models.EmailField(max_length=254)),
                ('location', models.TextField()),
                ('phone', models.CharField(max_length=16)),
            ],
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', django.contrib.sites.managers.CurrentSiteManager('site')),
            ],
        ),
    ]
