# Generated by Django 3.1.2 on 2020-12-28 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20201123_2117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacheruser',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
