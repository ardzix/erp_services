# Generated by Django 4.2.3 on 2023-08-10 16:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0025_alter_product_picture'),
        ('purchasing', '0009_alter_purchaseorder_approved_at_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='supplierproduct',
            unique_together={('supplier', 'product')},
        ),
    ]
