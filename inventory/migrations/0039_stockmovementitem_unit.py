# Generated by Django 4.2.3 on 2023-08-19 19:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0038_alter_stockmovement_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockmovementitem',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.unit'),
        ),
    ]
