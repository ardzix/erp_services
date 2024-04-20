# Generated by Django 4.2.3 on 2024-04-20 16:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('identities', '0003_contact_remove_companyprofile_approved_by_and_more'),
        ('purchasing', '0010_purchaseorder_discount_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplier',
            name='company_profile',
            field=models.ForeignKey(blank=True, help_text='Select the company profile for this supplier', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='suppliers_profile', to='identities.contact', verbose_name='Company Profile'),
        ),
    ]
