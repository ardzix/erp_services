# Generated by Django 4.2.3 on 2024-04-18 07:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0012_alter_file_file'),
        ('accounting', '0029_alter_financialreport_unique_together'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='financialentry',
            options={'ordering': ['order'], 'verbose_name': 'Financial Entry', 'verbose_name_plural': 'Financial Entries'},
        ),
        migrations.AlterModelOptions(
            name='financialreportentry',
            options={'ordering': ['entry__order'], 'verbose_name': 'Financial Report Entry', 'verbose_name_plural': 'Financial Report Entries'},
        ),
        migrations.AddField(
            model_name='financialreport',
            name='attachment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_attachment', to='common.file'),
        ),
    ]
