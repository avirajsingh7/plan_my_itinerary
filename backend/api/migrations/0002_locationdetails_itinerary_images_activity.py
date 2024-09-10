# Generated by Django 5.1.1 on 2024-09-09 18:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationDetails',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('street1', models.CharField(blank=True, max_length=255)),
                ('street2', models.CharField(blank=True, max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
                ('country', models.CharField(max_length=255)),
                ('postalcode', models.CharField(max_length=50)),
                ('address_string', models.TextField()),
                ('latitude', models.CharField(max_length=50)),
                ('longitude', models.CharField(max_length=50)),
                ('ranking', models.CharField(blank=True, max_length=50)),
                ('rating', models.CharField(blank=True, max_length=10)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Itinerary',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('total_days', models.IntegerField()),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Images',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('thumbnail', models.URLField(blank=True)),
                ('small', models.URLField(blank=True)),
                ('medium', models.URLField(blank=True)),
                ('large', models.URLField(blank=True)),
                ('original', models.URLField(blank=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('location_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.locationdetails')),
            ],
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('description', models.TextField()),
                ('duration', models.CharField(max_length=50)),
                ('day', models.CharField(max_length=50)),
                ('time_of_day', models.CharField(max_length=50)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('itinerary_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.itinerary')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.locationdetails')),
            ],
        ),
    ]
