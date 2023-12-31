# Generated by Django 4.2.3 on 2023-09-29 09:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_alter_administrativelvl4_name'),
        ('sales', '0008_remove_trip_driver_trip_vehicle'),
    ]

    operations = [
        migrations.AddField(
            model_name='customervisit',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customervisit',
            name='signature',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_signature', to='common.file'),
        ),
        migrations.AddField(
            model_name='customervisit',
            name='visit_evidence',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_visit_evidence', to='common.file'),
        ),
    ]
