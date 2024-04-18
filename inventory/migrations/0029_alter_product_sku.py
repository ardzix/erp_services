# Generated by Django 4.2.3 on 2024-04-18 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0028_alter_category_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='sku',
            field=models.CharField(blank=True, help_text='Enter the product stock keeping unit or barcode', max_length=100, null=True, unique=True),
        ),
    ]