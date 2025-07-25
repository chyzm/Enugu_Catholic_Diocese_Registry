# Generated by Django 4.2.23 on 2025-07-04 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0004_rename_date_of_death_parishioner_death_verification_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='parishioner',
            name='date_of_death',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='parishioner',
            name='death_details',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='parishioner',
            name='deceased',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='parishioner',
            name='marriage_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='parishioner',
            name='marriage_details',
            field=models.TextField(blank=True),
        ),
    ]
