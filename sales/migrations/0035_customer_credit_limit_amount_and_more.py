# Generated by Django 4.2.3 on 2024-03-12 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0034_salesorder_is_paid_alter_salesorder_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='credit_limit_amount',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Credit limit amount this customer can apply.', max_digits=19),
        ),
        migrations.AddField(
            model_name='customer',
            name='credit_limit_qty',
            field=models.PositiveIntegerField(blank=True, help_text='Total credit qty this customer can apply.', null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='due_date',
            field=models.PositiveIntegerField(blank=True, help_text='Due date of credit payment in day.', null=True),
        ),
    ]
