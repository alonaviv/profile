# Generated by Django 3.1.2 on 2020-12-28 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0005_auto_20201224_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='students',
            field=models.ManyToManyField(blank=True, related_name='classes', to='evaluations.Student'),
        ),
    ]
