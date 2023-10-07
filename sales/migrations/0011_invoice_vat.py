# Generated by Django 4.2.3 on 2023-10-07 21:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0010_salespayment_payment_evidence'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='vat',
            field=models.DecimalField(decimal_places=4, default=0.11, help_text='Value Added Tax percentage in decimal', max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
    ]
