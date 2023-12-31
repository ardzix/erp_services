# Generated by Django 4.2.3 on 2023-09-27 16:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdministrativeLvl1',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
            options={
                'verbose_name': 'Administrative Lvl 1',
            },
        ),
        migrations.CreateModel(
            name='AdministrativeLvl2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('lvl1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.administrativelvl1')),
            ],
            options={
                'verbose_name': 'Administrative Lvl 2',
            },
        ),
        migrations.CreateModel(
            name='AdministrativeLvl3',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('lvl2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.administrativelvl2')),
            ],
            options={
                'verbose_name': 'Administrative Lvl 3',
            },
        ),
        migrations.CreateModel(
            name='AdministrativeLvl4',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('lvl3', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.administrativelvl3')),
            ],
            options={
                'verbose_name': 'Administrative Lvl 4',
            },
        ),
    ]
