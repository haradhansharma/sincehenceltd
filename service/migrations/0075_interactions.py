# Generated by Django 4.2.2 on 2024-01-10 22:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('service', '0074_delete_interactions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('ans_required', models.BooleanField(default=True, verbose_name='Answer Required')),
                ('waited_for_reply', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('todo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='todo_interactions', to='service.projecttodo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contributor_interactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('created_at',),
            },
        ),
    ]
