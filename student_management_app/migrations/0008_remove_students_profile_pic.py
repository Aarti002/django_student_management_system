# Generated by Django 3.2.5 on 2021-07-24 17:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student_management_app', '0007_alter_leavereportstaff_leave_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='students',
            name='profile_pic',
        ),
    ]
