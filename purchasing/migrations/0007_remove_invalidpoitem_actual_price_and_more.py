# Generated by Django 4.2.3 on 2023-10-25 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchasing', '0006_invalidpoitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invalidpoitem',
            name='actual_price',
        ),
        migrations.AddField(
            model_name='invalidpoitem',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Enter the item price', max_digits=10, null=True),
        ),
    ]
