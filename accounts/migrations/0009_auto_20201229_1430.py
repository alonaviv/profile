# Generated by Django 3.1.2 on 2020-12-29 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20201229_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacheruser',
            name='pronoun_choice',
            field=models.CharField(choices=[('FEMALE', 'לשון נקבה'), ('MALE', 'לשון זכר'), ('NEUTRAL', 'לשון ניטרלית'), ('MIXED', 'לשון מעורבת')], max_length=30, null=True),
        ),
    ]
