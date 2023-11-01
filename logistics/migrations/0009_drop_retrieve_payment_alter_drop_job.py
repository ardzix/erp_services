# Generated by Django 4.2.3 on 2023-11-01 18:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0008_drop_status_job_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='drop',
            name='retrieve_payment',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='drop',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drops', to='logistics.job'),
        ),
    ]
