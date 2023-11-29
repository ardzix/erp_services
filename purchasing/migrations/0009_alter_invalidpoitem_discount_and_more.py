# Generated by Django 4.2.3 on 2023-11-29 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchasing', '0008_purchaseorder_invalid_item_evidence'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invalidpoitem',
            name='discount',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Enter the discount', max_digits=19, null=True),
        ),
        migrations.AlterField(
            model_name='invalidpoitem',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Enter the item price', max_digits=19, null=True),
        ),
        migrations.AlterField(
            model_name='purchaseorderitem',
            name='actual_price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Enter the actual item price', max_digits=19, null=True),
        ),
    ]
