# Generated by Django 4.2.23 on 2025-07-07 01:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0009_baptism_remove_parishioner_single_status_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='baptism',
            name='parishioner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='baptisms', to='registry.parishioner'),
        ),
    ]
