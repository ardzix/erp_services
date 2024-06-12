# Generated by Django 4.2.3 on 2024-04-03 16:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0018_transaction_number_transactioncategory_prefix'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journalentry',
            name='journal',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounting.account'),
        ),
    ]
