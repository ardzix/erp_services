# Generated by Django 4.2.3 on 2023-10-20 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_alter_stockmovementitem_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockmovementitem',
            name='destionation_movement_status',
            field=models.CharField(choices=[('waiting', 'Waiting for movement initiation'), ('on_progress', 'Item movement in progress'), ('on_check', 'Item movement awaiting verification'), ('put', 'Item placed in designated location'), ('checked', 'Item movement verified'), ('finished', 'Item movement completed')], default='waiting', help_text='Item movement status in destination warehouse', max_length=20),
        ),
        migrations.AddField(
            model_name='stockmovementitem',
            name='origin_movement_status',
            field=models.CharField(choices=[('waiting', 'Waiting for movement initiation'), ('on_progress', 'Item movement in progress'), ('on_check', 'Item movement awaiting verification'), ('put', 'Item placed in designated location'), ('checked', 'Item movement verified'), ('finished', 'Item movement completed')], default='waiting', help_text='Item movement status in origin warehouse', max_length=20),
        ),
    ]