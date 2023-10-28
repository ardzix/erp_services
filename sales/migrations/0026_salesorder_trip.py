# Generated by Django 4.2.3 on 2023-10-27 23:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0025_triptemplate_vehicles'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='trip',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sales.trip'),
        ),
    ]
