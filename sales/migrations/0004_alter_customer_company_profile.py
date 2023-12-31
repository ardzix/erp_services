# Generated by Django 4.2.3 on 2023-09-27 05:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('identities', '0001_initial'),
        ('sales', '0003_trip_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='company_profile',
            field=models.ForeignKey(blank=True, help_text='Select the company profile associated with the customer', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customers_profile', to='identities.companyprofile', verbose_name='Company Profile'),
        ),
    ]
