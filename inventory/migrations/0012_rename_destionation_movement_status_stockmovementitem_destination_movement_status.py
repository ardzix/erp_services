# Generated by Django 4.2.3 on 2023-10-20 22:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0011_stockmovementitem_destionation_movement_status_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stockmovementitem',
            old_name='destionation_movement_status',
            new_name='destination_movement_status',
        ),
    ]
