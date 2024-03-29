# Generated by Django 4.2.2 on 2023-11-13 23:43

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceCategory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(db_index=True, max_length=252)),
                ('description', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='service',
            name='categories',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_categories', to='service.servicecategory'),
        ),
    ]
