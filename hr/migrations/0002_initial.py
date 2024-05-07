# Generated by Django 4.2.3 on 2024-05-05 16:35

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('hr', '0001_initial'),
        ('identities', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('contact_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='identities.contact')),
                ('last_location', django.contrib.gis.db.models.fields.PointField(blank=True, help_text='Coordinates where the employee currently located', null=True, srid=4326)),
                ('department', models.ForeignKey(blank=True, help_text='The department the employee belongs to', null=True, on_delete=django.db.models.deletion.SET_NULL, to='hr.department')),
                ('user', models.OneToOneField(help_text='The associated user of the employee', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Employee',
                'verbose_name_plural': 'Employees',
                'ordering': ['-id'],
            },
            bases=('identities.contact',),
        ),
        migrations.CreateModel(
            name='Performance',
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
                ('rating', models.PositiveIntegerField(choices=[(1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')], help_text="Rating given to the employee's performance")),
                ('review', models.TextField(blank=True, help_text='Additional review notes')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_approved_by', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_deleted_by', to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(help_text='The employee being reviewed', on_delete=django.db.models.deletion.CASCADE, to='hr.employee')),
                ('owned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_owner', to=settings.AUTH_USER_MODEL)),
                ('published_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_published_by', to=settings.AUTH_USER_MODEL)),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_site', to='sites.site')),
                ('unapproved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unapproved_by', to=settings.AUTH_USER_MODEL)),
                ('unpublished_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unpublished_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Performance',
                'verbose_name_plural': 'Performances',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='LocationTracker',
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
                ('location', django.contrib.gis.db.models.fields.PointField(help_text='Coordinates where the employee located', null=True, srid=4326)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_approved_by', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_deleted_by', to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(blank=True, help_text='The employee being traked', null=True, on_delete=django.db.models.deletion.CASCADE, to='hr.employee')),
                ('owned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_owner', to=settings.AUTH_USER_MODEL)),
                ('published_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_published_by', to=settings.AUTH_USER_MODEL)),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_site', to='sites.site')),
                ('unapproved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unapproved_by', to=settings.AUTH_USER_MODEL)),
                ('unpublished_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unpublished_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Location Tracker',
                'verbose_name_plural': 'Location Trackers',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Leave',
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
                ('leave_type', models.CharField(help_text='The type of leave', max_length=100)),
                ('start_date', models.DateField(help_text='Start date of the leave')),
                ('end_date', models.DateField(help_text='End date of the leave')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', help_text='The status of the leave request', max_length=20)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_approved_by', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_deleted_by', to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(help_text='The employee who requested the leave', on_delete=django.db.models.deletion.CASCADE, to='hr.employee')),
                ('owned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_owner', to=settings.AUTH_USER_MODEL)),
                ('published_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_published_by', to=settings.AUTH_USER_MODEL)),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_site', to='sites.site')),
                ('unapproved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unapproved_by', to=settings.AUTH_USER_MODEL)),
                ('unpublished_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unpublished_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Leave',
                'verbose_name_plural': 'Leaves',
                'ordering': ['-id'],
            },
        ),
        migrations.AddField(
            model_name='department',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_approved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='department',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='department',
            name='deleted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_deleted_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='department',
            name='owned_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='department',
            name='published_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_published_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='department',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_site', to='sites.site'),
        ),
        migrations.AddField(
            model_name='department',
            name='unapproved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unapproved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='department',
            name='unpublished_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unpublished_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='department',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='attendance',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_approved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='attendance',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='attendance',
            name='deleted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_deleted_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='attendance',
            name='employee',
            field=models.ForeignKey(help_text='The employee whose attendance is recorded', on_delete=django.db.models.deletion.CASCADE, to='hr.employee'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='owned_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='attendance',
            name='published_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_published_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='attendance',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_site', to='sites.site'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='unapproved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unapproved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='attendance',
            name='unpublished_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unpublished_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='attendance',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL),
        ),
    ]