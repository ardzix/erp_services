# Generated by Django 4.2.3 on 2023-09-27 18:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_alter_administrativelvl4_name'),
        ('sales', '0006_rename_r2_customer_rw'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='id_card',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_id_card', to='common.file'),
        ),
        migrations.AddField(
            model_name='customer',
            name='signature',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_signature', to='common.file'),
        ),
        migrations.AddField(
            model_name='customer',
            name='store_front',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_store_front', to='common.file'),
        ),
        migrations.AddField(
            model_name='customer',
            name='store_street',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_store_street', to='common.file'),
        ),
    ]
