# Generated by Django 4.2.3 on 2023-10-19 09:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0019_alter_customer_options_alter_customervisit_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customervisit',
            options={'ordering': ['order'], 'verbose_name': 'Customer Visit', 'verbose_name_plural': 'Customer Visits'},
        ),
    ]
