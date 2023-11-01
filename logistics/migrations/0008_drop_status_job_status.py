# Generated by Django 4.2.3 on 2023-11-01 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0007_drop'),
    ]

    operations = [
        migrations.AddField(
            model_name='drop',
            name='status',
            field=models.CharField(choices=[('waiting', 'Waiting'), ('on_progress', 'On Progress'), ('arrived', 'Arrived'), ('completed', 'Completed'), ('skipped', 'Skipped')], default='waiting', max_length=50),
        ),
        migrations.AddField(
            model_name='job',
            name='status',
            field=models.CharField(choices=[('waiting', 'Waiting'), ('on_progress', 'On Progress'), ('arrived', 'Arrived'), ('completed', 'Completed'), ('skipped', 'Skipped')], default='waiting', max_length=50),
        ),
    ]
