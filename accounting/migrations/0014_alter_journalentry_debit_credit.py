# Generated by Django 4.2.3 on 2024-03-28 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0013_remove_transaction_external_id32_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journalentry',
            name='debit_credit',
            field=models.CharField(blank=True, choices=[('DEBIT', 'Debit'), ('CREDIT', 'Credit')], max_length=10, null=True),
        ),
    ]