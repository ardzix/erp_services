# Generated by Django 4.2.3 on 2024-03-27 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0011_remove_account_parent_category_account_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='number',
            field=models.CharField(default=1, help_text='Enter account number', max_length=20),
            preserve_default=False,
        ),
    ]
