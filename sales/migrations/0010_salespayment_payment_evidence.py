# Generated by Django 4.2.3 on 2023-10-07 20:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_alter_administrativelvl4_name'),
        ('sales', '0009_customervisit_notes_customervisit_signature_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='salespayment',
            name='payment_evidence',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_payment_evidence', to='common.file'),
        ),
    ]
