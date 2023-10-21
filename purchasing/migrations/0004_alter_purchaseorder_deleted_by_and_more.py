# Generated by Django 4.2.3 on 2023-10-21 00:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('purchasing', '0003_alter_purchaseorder_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseorder',
            name='deleted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_deleted_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='owned_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='published_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_published_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='unapproved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unapproved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='unpublished_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unpublished_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='purchaseorderitem',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_approved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='purchaseorderitem',
            name='deleted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_deleted_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='purchaseorderitem',
            name='owned_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='purchaseorderitem',
            name='published_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_published_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='purchaseorderitem',
            name='unapproved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unapproved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='purchaseorderitem',
            name='unpublished_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unpublished_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='purchaseorderitem',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_approved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='deleted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_deleted_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='owned_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='published_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_published_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='unapproved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unapproved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='unpublished_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unpublished_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_approved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='deleted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_deleted_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='owned_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='published_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_published_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='unapproved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unapproved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='unpublished_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unpublished_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supplierproduct',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_approved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supplierproduct',
            name='deleted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_deleted_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supplierproduct',
            name='owned_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supplierproduct',
            name='published_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_published_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supplierproduct',
            name='unapproved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unapproved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supplierproduct',
            name='unpublished_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unpublished_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supplierproduct',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='vendorperformance',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_approved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='vendorperformance',
            name='deleted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_deleted_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='vendorperformance',
            name='owned_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='vendorperformance',
            name='published_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_published_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='vendorperformance',
            name='unapproved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unapproved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='vendorperformance',
            name='unpublished_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unpublished_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='vendorperformance',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
