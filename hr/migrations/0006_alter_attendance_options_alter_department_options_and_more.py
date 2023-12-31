# Generated by Django 4.2.3 on 2023-11-06 21:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0005_alter_attendance_approved_by_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attendance',
            options={'ordering': ['-id'], 'verbose_name': 'Attendance', 'verbose_name_plural': 'Attendances'},
        ),
        migrations.AlterModelOptions(
            name='department',
            options={'ordering': ['-id'], 'verbose_name': 'Department', 'verbose_name_plural': 'Departments'},
        ),
        migrations.AlterModelOptions(
            name='employee',
            options={'ordering': ['-id'], 'verbose_name': 'Employee', 'verbose_name_plural': 'Employees'},
        ),
        migrations.AlterModelOptions(
            name='leave',
            options={'ordering': ['-id'], 'verbose_name': 'Leave', 'verbose_name_plural': 'Leaves'},
        ),
        migrations.AlterModelOptions(
            name='performance',
            options={'ordering': ['-id'], 'verbose_name': 'Performance', 'verbose_name_plural': 'Performances'},
        ),
    ]
