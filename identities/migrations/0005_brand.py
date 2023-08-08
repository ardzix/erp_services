# Generated by Django 4.2.3 on 2023-08-07 04:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('identities', '0004_rename_id62_companyprofile_id32_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
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
                ('name', models.CharField(help_text='Enter the brand name', max_length=100)),
                ('description', models.TextField(blank=True, help_text='Enter the brand description')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_approved_by', to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='identities.companyprofile')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_deleted_by', to=settings.AUTH_USER_MODEL)),
                ('owned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_owner', to=settings.AUTH_USER_MODEL)),
                ('published_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_published_by', to=settings.AUTH_USER_MODEL)),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_site', to='sites.site')),
                ('unapproved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_unapproved_by', to=settings.AUTH_USER_MODEL)),
                ('unpublished_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_unpublished_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Brand',
                'verbose_name_plural': 'Brands',
            },
        ),
    ]
