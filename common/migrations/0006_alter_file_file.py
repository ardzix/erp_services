# Generated by Django 4.2.3 on 2023-11-17 00:07

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0005_configuration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='file',
            field=models.FileField(blank=True, max_length=300, null=True, storage=django.core.files.storage.FileSystemStorage(base_url='http://127.0.0.1:8000/static/upload/file/', location='/home/ardz/Documents/erp/erp_services/static/upload/file'), upload_to=''),
        ),
    ]