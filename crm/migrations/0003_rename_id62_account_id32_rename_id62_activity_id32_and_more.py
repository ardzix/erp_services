# Generated by Django 4.2.3 on 2023-07-12 16:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_alter_account_owned_at_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='id62',
            new_name='id32',
        ),
        migrations.RenameField(
            model_name='activity',
            old_name='id62',
            new_name='id32',
        ),
        migrations.RenameField(
            model_name='contact',
            old_name='id62',
            new_name='id32',
        ),
        migrations.RenameField(
            model_name='lead',
            old_name='id62',
            new_name='id32',
        ),
        migrations.RenameField(
            model_name='opportunity',
            old_name='id62',
            new_name='id32',
        ),
    ]