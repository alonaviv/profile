# Generated by Django 3.1.2 on 2021-12-19 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0013_evaluation_is_submitted'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]