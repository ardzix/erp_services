# Generated by Django 4.2.3 on 2023-08-10 15:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_rename_id62_file_id32'),
        ('inventory', '0024_product_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='picture',
            field=models.ForeignKey(blank=True, help_text='Picture for the product', null=True, on_delete=django.db.models.deletion.SET_NULL, to='common.file'),
        ),
    ]