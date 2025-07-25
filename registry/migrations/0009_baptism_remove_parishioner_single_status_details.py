# Generated by Django 4.2.23 on 2025-07-07 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0008_remove_user_groups_remove_user_user_permissions_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Baptism',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('child_name', models.CharField(max_length=255)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=1)),
                ('date_of_birth', models.DateField()),
                ('time_of_birth', models.TimeField()),
                ('place_of_birth', models.CharField(max_length=255)),
                ('hospital_name', models.CharField(blank=True, max_length=255, null=True)),
                ('birth_parish', models.CharField(max_length=100)),
                ('baptism_date', models.DateField(blank=True, null=True)),
                ('baptism_certificate', models.CharField(blank=True, max_length=50, null=True)),
                ('father_name', models.CharField(max_length=255)),
                ('father_religion', models.CharField(max_length=50)),
                ('father_phone', models.CharField(max_length=20)),
                ('father_parish', models.CharField(blank=True, max_length=100, null=True)),
                ('mother_name', models.CharField(max_length=255)),
                ('mother_maiden', models.CharField(blank=True, max_length=255, null=True)),
                ('mother_religion', models.CharField(max_length=50)),
                ('mother_phone', models.CharField(max_length=20)),
                ('mother_parish', models.CharField(blank=True, max_length=100, null=True)),
                ('home_address', models.TextField()),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='parishioner',
            name='single_status_details',
        ),
    ]
