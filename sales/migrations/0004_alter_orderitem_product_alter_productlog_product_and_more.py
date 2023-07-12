# Generated by Django 4.2.3 on 2023-07-11 10:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_delete_productlog'),
        ('sales', '0003_productlog_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(help_text='Select the product associated with the item', on_delete=django.db.models.deletion.CASCADE, to='inventory.product'),
        ),
        migrations.AlterField(
            model_name='productlog',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='inventory.product'),
        ),
        migrations.DeleteModel(
            name='Product',
        ),
    ]
