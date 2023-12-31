# Generated by Django 4.2.3 on 2023-10-17 05:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('inventory', '0006_alter_stockmovement_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockmovement',
            name='creator_id',
            field=models.PositiveIntegerField(blank=True, help_text='Enter the ID of the creator instance', null=True),
        ),
        migrations.AddField(
            model_name='stockmovement',
            name='creator_type',
            field=models.ForeignKey(blank=True, help_text='Select the content type of the creator instance', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='creator_stockmovement_set', related_query_name='creator_stockmovement', to='contenttypes.contenttype'),
        ),
    ]
