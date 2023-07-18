# Generated by Django 4.2.3 on 2023-07-12 15:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('purchasing', '0005_alter_purchaseorder_approved_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseorder',
            name='approved_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Approved at'),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_purchase_orders', to=settings.AUTH_USER_MODEL, verbose_name='Approved by'),
        ),
    ]