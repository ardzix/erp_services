# Generated by Django 4.2.3 on 2023-11-14 02:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0030_trip_collector'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='vat',
            field=models.DecimalField(decimal_places=4, help_text='Value Added Tax percentage in decimal', max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
    ]
