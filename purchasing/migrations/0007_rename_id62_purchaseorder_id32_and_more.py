# Generated by Django 4.2.3 on 2023-07-12 16:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchasing', '0006_alter_purchaseorder_approved_at_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchaseorder',
            old_name='id62',
            new_name='id32',
        ),
        migrations.RenameField(
            model_name='purchaseorderitem',
            old_name='id62',
            new_name='id32',
        ),
        migrations.RenameField(
            model_name='shipment',
            old_name='id62',
            new_name='id32',
        ),
        migrations.RenameField(
            model_name='supplier',
            old_name='id62',
            new_name='id32',
        ),
        migrations.RenameField(
            model_name='vendorperformance',
            old_name='id62',
            new_name='id32',
        ),
    ]