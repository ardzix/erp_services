# Generated by Django 4.2.3 on 2023-09-28 06:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0002_vehicle_warehaouse'),
        ('sales', '0007_customer_id_card_customer_signature_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trip',
            name='driver',
        ),
        migrations.AddField(
            model_name='trip',
            name='vehicle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='logistics.vehicle'),
        ),
    ]