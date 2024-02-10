# Generated by Django 4.2.3 on 2023-11-29 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_alter_account_approved_by_alter_account_deleted_by_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opportunity',
            name='value',
            field=models.DecimalField(decimal_places=2, help_text='The value of the opportunity', max_digits=19),
        ),
    ]