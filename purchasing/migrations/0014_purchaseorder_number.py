# Generated by Django 4.2.3 on 2024-05-05 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchasing', '0013_remove_supplier_company_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='number',
            field=models.CharField(blank=True, help_text='Enter account number', max_length=20, null=True, unique=True),
        ),
    ]
