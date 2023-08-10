# Generated by Django 4.2.3 on 2023-08-10 15:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('identities', '0006_alter_brand_company_alter_companyprofile_address_and_more'),
        ('purchasing', '0008_supplierproduct'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseorder',
            name='approved_at',
            field=models.DateTimeField(blank=True, help_text='Specify the date and time when the order was approved', null=True, verbose_name='Approved at'),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='approved_by',
            field=models.ForeignKey(blank=True, help_text='Select the user who approved the purchase order', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_purchase_orders', to=settings.AUTH_USER_MODEL, verbose_name='Approved by'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='company_profile',
            field=models.ForeignKey(help_text='Select the company profile for this supplier', on_delete=django.db.models.deletion.CASCADE, related_name='suppliers_profile', to='identities.companyprofile', verbose_name='Company Profile'),
        ),
    ]
