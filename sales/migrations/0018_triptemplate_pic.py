# Generated by Django 4.2.3 on 2023-10-17 08:46

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sales', '0017_customervisit_item_delivery_evidence'),
    ]

    operations = [
        migrations.AddField(
            model_name='triptemplate',
            name='pic',
            field=models.ManyToManyField(blank=True, help_text='Select people in charge of this trip', to=settings.AUTH_USER_MODEL),
        ),
    ]
