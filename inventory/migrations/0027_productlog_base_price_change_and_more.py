# Generated by Django 4.2.3 on 2023-08-13 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0026_stockmovementitem_buy_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='productlog',
            name='base_price_change',
            field=models.IntegerField(blank=True, help_text='Enter the base price change', null=True),
        ),
        migrations.AddField(
            model_name='productlog',
            name='buy_price_change',
            field=models.IntegerField(blank=True, help_text='Enter the buy price change', null=True),
        ),
        migrations.AlterField(
            model_name='productlog',
            name='quantity_change',
            field=models.IntegerField(blank=True, help_text='Enter the quantity change', null=True),
        ),
    ]
