# Generated by Django 3.2.5 on 2021-08-08 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student_management_app', '0012_alter_leavereportstudent_leave_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffs',
            name='fcm_token',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='students',
            name='fcm_token',
            field=models.TextField(default=''),
        ),
    ]
