# Generated by Django 3.1.2 on 2020-12-24 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0004_auto_20201224_0944'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluation',
            name='trimester',
            field=models.CharField(choices=[('FIRST_TRIMESTER', 'FIRST_TRIMESTER'), ('SECOND_TRIMESTER', 'SECOND_TRIMESTER'), ('THIRD_TRIMESTER', 'THIRD_TRIMESTER'), ('NULL_TRIMESTER', 'NULL_TRIMESTER')], max_length=20),
        ),
    ]
