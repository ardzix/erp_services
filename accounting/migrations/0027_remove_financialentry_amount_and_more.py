# Generated by Django 4.2.3 on 2024-04-18 04:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sites', '0002_alter_domain_unique'),
        ('accounting', '0026_alter_financialentry_amount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='financialentry',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='financialentry',
            name='financial_report',
        ),
        migrations.AddField(
            model_name='financialentry',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounting.accountcategory'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='financialentry',
            name='financial_statement',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounting.financialstatement'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='financialentry',
            name='order',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='financialstatement',
            name='accounts',
            field=models.ManyToManyField(through='accounting.FinancialEntry', to='accounting.account'),
        ),
        migrations.CreateModel(
            name='FinancialReportEntry',
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
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.account')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_approved_by', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.accountcategory')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_deleted_by', to=settings.AUTH_USER_MODEL)),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.financialentry')),
                ('financial_report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.financialreport')),
                ('owned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_owner', to=settings.AUTH_USER_MODEL)),
                ('published_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_published_by', to=settings.AUTH_USER_MODEL)),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_site', to='sites.site')),
                ('unapproved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unapproved_by', to=settings.AUTH_USER_MODEL)),
                ('unpublished_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_unpublished_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Financial Report Entry',
                'verbose_name_plural': 'Financial Report Entries',
                'ordering': ['-id'],
            },
        ),
    ]
