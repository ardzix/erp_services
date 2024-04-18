# Generated by Django 4.2.3 on 2024-03-28 04:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('accounting', '0012_account_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='external_id32',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='generate_journal',
        ),
        migrations.AddField(
            model_name='journalentry',
            name='account',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounting.account'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='journalentry',
            name='is_allocation',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='allocations',
            field=models.ManyToManyField(help_text='Select journal entry as allocations', related_name='account_allocations', through='accounting.JournalEntry', to='accounting.account'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='origin_id',
            field=models.PositiveIntegerField(blank=True, help_text='Enter the ID of the origin', null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='origin_type',
            field=models.ForeignKey(blank=True, help_text='Select the content type of the origin', null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(choices=[('cash_in', 'Cash In'), ('cash_out', 'Cash Out')], default='cash_in', max_length=20),
        ),
    ]