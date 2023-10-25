# Generated by Django 4.2.3 on 2023-10-25 15:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0005_remove_job_stock_movement_job_trip'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 10, 25, 15, 37, 34, 756318, tzinfo=datetime.timezone.utc), help_text='Date for the job trip', verbose_name='Date'),
            preserve_default=False,
        ),
    ]
