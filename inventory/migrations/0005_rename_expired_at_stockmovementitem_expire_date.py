# Generated by Django 4.2.3 on 2023-10-07 18:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_stockmovementitem_expired_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stockmovementitem',
            old_name='expired_at',
            new_name='expire_date',
        ),
    ]
