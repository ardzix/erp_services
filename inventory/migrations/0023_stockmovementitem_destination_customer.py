# Generated by Django 4.2.3 on 2023-12-01 01:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0032_alter_orderitem_price'),
        ('inventory', '0022_alter_product_base_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockmovementitem',
            name='destination_customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sales.customer'),
        ),
    ]
