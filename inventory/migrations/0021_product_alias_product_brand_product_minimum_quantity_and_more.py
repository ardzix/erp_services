# Generated by Django 4.2.3 on 2023-08-07 04:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('identities', '0005_brand'),
        ('sites', '0002_alter_domain_unique'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventory', '0020_alter_stockmovementitem_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='alias',
            field=models.CharField(blank=True, help_text='Enter the product alias name', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(blank=True, help_text='Select the product brand', null=True, on_delete=django.db.models.deletion.SET_NULL, to='identities.brand'),
        ),
        migrations.AddField(
            model_name='product',
            name='minimum_quantity',
            field=models.PositiveIntegerField(default=0, help_text='Enter the minimum quantity at which the product needs to be restocked'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_type',
            field=models.CharField(choices=[('raw_material', 'Raw Material - Used to create other products'), ('finished_goods', 'Finished Goods - Completed and ready for sale'), ('intermediate', 'Intermediate Product - Partly finished, used in production'), ('consumable', 'Consumable - Used in the production process but not part of the final product')], default='finished_goods', help_text='Select the product type', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='sku',
            field=models.CharField(default=1, help_text='Enter the product stock keeping unit or barcode', max_length=100),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nonce', models.CharField(blank=True, max_length=128, null=True)),
                ('id32', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(db_index=True)),
                ('created_at_timestamp', models.PositiveIntegerField(db_index=True)),
                ('owned_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('owned_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('updated_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('published_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('unpublished_at', models.DateTimeField(blank=True, null=True)),
                ('unpublished_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('approved_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('unapproved_at', models.DateTimeField(blank=True, null=True)),
                ('unapproved_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('deleted_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('name', models.CharField(help_text='Enter the unit name', max_length=100)),
                ('symbol', models.CharField(help_text='Enter the unit symbol', max_length=10)),
                ('conversion_factor', models.DecimalField(decimal_places=4, default=1, help_text='Conversion factor to parent unit', max_digits=10)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_approved_by', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_deleted_by', to=settings.AUTH_USER_MODEL)),
                ('owned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_owner', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, help_text='Select the parent unit', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subunits', to='inventory.unit')),
                ('published_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_published_by', to=settings.AUTH_USER_MODEL)),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_site', to='sites.site')),
                ('unapproved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_unapproved_by', to=settings.AUTH_USER_MODEL)),
                ('unpublished_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_unpublished_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Unit',
                'verbose_name_plural': 'Units',
            },
        ),
        migrations.CreateModel(
            name='ProductLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nonce', models.CharField(blank=True, max_length=128, null=True)),
                ('id32', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(db_index=True)),
                ('created_at_timestamp', models.PositiveIntegerField(db_index=True)),
                ('owned_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('owned_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('updated_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('published_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('unpublished_at', models.DateTimeField(blank=True, null=True)),
                ('unpublished_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('approved_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('unapproved_at', models.DateTimeField(blank=True, null=True)),
                ('unapproved_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('deleted_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('area', models.CharField(help_text='Enter the area within the warehouse', max_length=100)),
                ('shelving', models.CharField(help_text='Enter the shelving within the area', max_length=100)),
                ('position', models.CharField(help_text='Enter the specific position on the shelving', max_length=100)),
                ('quantity', models.PositiveIntegerField(default=0, help_text='Enter the product quantity in this location')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_approved_by', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_deleted_by', to=settings.AUTH_USER_MODEL)),
                ('owned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_owner', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(help_text='Select the product', on_delete=django.db.models.deletion.CASCADE, to='inventory.product')),
                ('published_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_published_by', to=settings.AUTH_USER_MODEL)),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_site', to='sites.site')),
                ('unapproved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_unapproved_by', to=settings.AUTH_USER_MODEL)),
                ('unpublished_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_unpublished_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL)),
                ('warehouse', models.ForeignKey(help_text='Select the warehouse', on_delete=django.db.models.deletion.CASCADE, to='inventory.warehouse')),
            ],
            options={
                'verbose_name': 'Product Location',
                'verbose_name_plural': 'Product Locations',
            },
        ),
        migrations.CreateModel(
            name='ProductGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nonce', models.CharField(blank=True, max_length=128, null=True)),
                ('id32', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(db_index=True)),
                ('created_at_timestamp', models.PositiveIntegerField(db_index=True)),
                ('owned_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('owned_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('updated_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('published_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('unpublished_at', models.DateTimeField(blank=True, null=True)),
                ('unpublished_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('approved_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('unapproved_at', models.DateTimeField(blank=True, null=True)),
                ('unapproved_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('deleted_at_timestamp', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('name', models.CharField(help_text='Enter the product name', max_length=100)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_approved_by', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_deleted_by', to=settings.AUTH_USER_MODEL)),
                ('owned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_owner', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, help_text='Select the parent group', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subgroups', to='inventory.productgroup')),
                ('products', models.ManyToManyField(to='inventory.product')),
                ('published_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_published_by', to=settings.AUTH_USER_MODEL)),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_site', to='sites.site')),
                ('unapproved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_unapproved_by', to=settings.AUTH_USER_MODEL)),
                ('unpublished_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_unpublished_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Product Group',
                'verbose_name_plural': 'Product Groups',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='purchasing_unit',
            field=models.ForeignKey(blank=True, default=None, help_text='Select the purchasing unit for the product', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products_as_purchasing', to='inventory.unit'),
        ),
        migrations.AddField(
            model_name='product',
            name='sales_unit',
            field=models.ForeignKey(blank=True, default=None, help_text='Select the sales unit for the product', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products_as_sales', to='inventory.unit'),
        ),
        migrations.AddField(
            model_name='product',
            name='smallest_unit',
            field=models.ForeignKey(blank=True, default=None, help_text='Select the smallest unit for the product', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products_as_smallest', to='inventory.unit'),
        ),
        migrations.AddField(
            model_name='product',
            name='stock_unit',
            field=models.ForeignKey(blank=True, default=None, help_text='Select the stock unit for the product', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products_as_stock', to='inventory.unit'),
        ),
    ]
