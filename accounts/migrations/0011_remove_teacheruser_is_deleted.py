# Generated by Django 3.1.2 on 2021-01-07 09:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_teacheruser_is_deleted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacheruser',
            name='is_deleted',
        ),
    ]