# Generated by Django 5.2.4 on 2025-07-04 00:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Parishioner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.CharField(blank=True, max_length=20, unique=True)),
                ('full_name', models.CharField(max_length=255)),
                ('title', models.CharField(blank=True, max_length=50)),
                ('date_of_birth', models.DateField()),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=1)),
                ('marital_status', models.CharField(choices=[('S', 'Single'), ('M', 'Married'), ('D', 'Divorced'), ('W', 'Widowed')], max_length=1)),
                ('phone_number', models.CharField(max_length=20)),
                ('parish', models.CharField(max_length=100)),
                ('station', models.CharField(max_length=100)),
                ('baptized', models.BooleanField(default=False)),
                ('baptism_date', models.DateField(blank=True, null=True)),
                ('confirmed', models.BooleanField(default=False)),
                ('confirmation_date', models.DateField(blank=True, null=True)),
                ('first_communion', models.BooleanField(default=False)),
                ('first_communion_date', models.DateField(blank=True, null=True)),
                ('education_level', models.CharField(choices=[('PRIMARY', 'Primary'), ('SECONDARY', 'Secondary'), ('TERTIARY', 'Tertiary'), ('OTHER', 'Other')], max_length=20)),
                ('occupation', models.CharField(max_length=100)),
                ('employment_status', models.CharField(choices=[('EMPLOYED', 'Employed'), ('SELF_EMPLOYED', 'Self Employed'), ('UNEMPLOYED', 'Unemployed')], max_length=20)),
                ('family_details', models.TextField(blank=True)),
                ('marriage_details', models.TextField(blank=True)),
                ('marriage_date', models.DateField(blank=True, null=True)),
                ('deceased', models.BooleanField(default=False)),
                ('date_of_death', models.DateField(blank=True, null=True)),
                ('death_details', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
