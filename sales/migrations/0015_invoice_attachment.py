# Generated by Django 4.2.3 on 2023-10-13 02:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_alter_administrativelvl4_name'),
        ('sales', '0014_salesorder_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='attachment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_attachment', to='common.file'),
        ),
    ]