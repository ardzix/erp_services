# Generated by Django 4.2.3 on 2024-05-04 19:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('purchasing', '0013_remove_supplier_company_profile'),
        ('inventory', '0029_alter_product_sku'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockmovement',
            name='purchase_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='purchasing.purchaseorder'),
        ),
    ]