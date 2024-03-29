# Generated by Django 4.2.2 on 2024-01-07 22:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0026_userverificationrequest'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userverificationrequest',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterField(
            model_name='userverificationrequest',
            name='status',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, related_name='verification_approvals', to='accounts.approvalstatus'),
        ),
    ]
