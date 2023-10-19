# Generated by Django 4.2.3 on 2023-10-19 04:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0008_remove_product_sales_unit_remove_product_stock_unit'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['-id'], 'verbose_name': 'Category', 'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['-id'], 'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
        migrations.AlterModelOptions(
            name='productgroup',
            options={'ordering': ['-id'], 'verbose_name': 'Product Group', 'verbose_name_plural': 'Product Groups'},
        ),
        migrations.AlterModelOptions(
            name='productlocation',
            options={'ordering': ['-id'], 'verbose_name': 'Product Location', 'verbose_name_plural': 'Product Locations'},
        ),
        migrations.AlterModelOptions(
            name='productlog',
            options={'ordering': ['-id'], 'verbose_name': 'Product Log', 'verbose_name_plural': 'Product Logs'},
        ),
        migrations.AlterModelOptions(
            name='replenishmentorder',
            options={'ordering': ['-id'], 'verbose_name': 'Replenishment Order', 'verbose_name_plural': 'Replenishment Orders'},
        ),
        migrations.AlterModelOptions(
            name='replenishmentreceived',
            options={'ordering': ['-id'], 'verbose_name': 'Replenishment Received', 'verbose_name_plural': 'Replenishment Received'},
        ),
        migrations.AlterModelOptions(
            name='stockadjustment',
            options={'ordering': ['-id'], 'verbose_name': 'Stock Adjustment', 'verbose_name_plural': 'Stock Adjustments'},
        ),
        migrations.AlterModelOptions(
            name='stockmovement',
            options={'ordering': ['-id'], 'verbose_name': 'Stock Movement', 'verbose_name_plural': 'Stock Movements'},
        ),
        migrations.AlterModelOptions(
            name='stockmovementitem',
            options={'ordering': ['-id'], 'verbose_name': 'Stock Movement Item', 'verbose_name_plural': 'Stock Movement Items'},
        ),
        migrations.AlterModelOptions(
            name='unit',
            options={'ordering': ['-id'], 'verbose_name': 'Unit', 'verbose_name_plural': 'Units'},
        ),
        migrations.AlterModelOptions(
            name='warehouse',
            options={'ordering': ['-id'], 'verbose_name': 'Warehouse', 'verbose_name_plural': 'Warehouses'},
        ),
        migrations.AlterModelOptions(
            name='warehousestock',
            options={'ordering': ['-id'], 'verbose_name': 'Warehouse Stock', 'verbose_name_plural': 'Warehouse Stocks'},
        ),
    ]
