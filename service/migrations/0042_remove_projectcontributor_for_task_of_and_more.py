# Generated by Django 4.2.2 on 2024-01-02 10:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_experttype'),
        ('service', '0041_alter_projectcontributor_for_task_of'),
    ]

    operations = [
        # migrations.RemoveField(
        #     model_name='projectcontributor',
        #     name='for_task_of',
        # ),
        # migrations.AlterField(
        #     model_name='projecttodo',
        #     name='m_type',
        #     field=models.ForeignKey(blank=True, max_length=100, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.experttype'),
        # ),
        # migrations.AddField(
        #     model_name='projectcontributor',
        #     name='for_task_of',
        #     field=models.ManyToManyField(related_name='contributors_of_expertise', to='accounts.experttype'),
        # ),
    ]
