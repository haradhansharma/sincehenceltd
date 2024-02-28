# Generated by Django 4.2.2 on 2023-11-16 08:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0005_blogcomments_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogcomments',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child', to='cms.blogcomments'),
        ),
    ]
