# Generated by Django 4.2.3 on 2023-12-06 07:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0012_driver_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DriverMovement',
        ),
    ]
