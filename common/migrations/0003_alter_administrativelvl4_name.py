# Generated by Django 4.2.3 on 2023-09-27 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_administrativelvl1_administrativelvl2_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='administrativelvl4',
            name='name',
            field=models.CharField(max_length=140),
        ),
    ]
