# Generated by Django 4.2.3 on 2023-10-20 13:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_alter_category_options_alter_product_options_and_more'),
        ('sales', '0020_alter_customervisit_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='warehouse',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.warehouse'),
        ),
    ]
