# Generated by Django 4.2.3 on 2023-11-01 09:19

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0004_alter_file_approved_by_alter_file_deleted_by_and_more'),
        ('logistics', '0006_job_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Drop',
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
                ('location_name', models.CharField(help_text="Enter the location's name", max_length=100)),
                ('address', models.TextField(help_text='Enter the address')),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, help_text='Enter the location coordinates', null=True, srid=4326)),
                ('order', models.PositiveIntegerField(help_text='Order of drop in the job', verbose_name='Order')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_approved_by', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_deleted_by', to=settings.AUTH_USER_MODEL)),
                ('item_delivery_evidence', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_item_delivery_evidence', to='common.file')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='logistics.job')),
                ('owned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_owner', to=settings.AUTH_USER_MODEL)),
                ('published_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_published_by', to=settings.AUTH_USER_MODEL)),
                ('signature', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_signature', to='common.file')),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_site', to='sites.site')),
                ('travel_document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_travel_document', to='common.file')),
                ('unapproved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unapproved_by', to=settings.AUTH_USER_MODEL)),
                ('unpublished_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unpublished_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL)),
                ('visit_evidence', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_visit_evidence', to='common.file')),
            ],
            options={
                'verbose_name': 'Drop',
                'verbose_name_plural': 'Drops',
                'ordering': ['order'],
            },
        ),
    ]