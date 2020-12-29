# Generated by Django 3.1.2 on 2020-12-29 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20201229_1323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacheruser',
            name='pronoun_choice',
            field=models.CharField(choices=[('MALE', 'לשון זכר'), ('FEMALE', 'לשון נקבה'), ('NEUTRAL', 'לשון ניטרלית'), ('MIXED', 'לשון מעורבבת')], max_length=30, null=True),
        ),
    ]
