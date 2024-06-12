# Generated by Django 4.2.3 on 2024-04-27 00:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0042_recievable_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Enter the payment amount', max_digits=19, null=True),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='is_paid_in_terms',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='vat',
            field=models.DecimalField(decimal_places=4, default=0, help_text='Value Added Tax percentage in decimal', max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
    ]
