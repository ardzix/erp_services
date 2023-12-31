# Generated by Django 4.2.3 on 2023-10-25 15:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0024_trip_is_delivery_processed'),
        ('logistics', '0004_alter_driver_approved_by_alter_driver_deleted_by_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='stock_movement',
        ),
        migrations.AddField(
            model_name='job',
            name='trip',
            field=models.ForeignKey(default=1, help_text='Select the trip for this job', on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='sales.trip'),
            preserve_default=False,
        ),
    ]
