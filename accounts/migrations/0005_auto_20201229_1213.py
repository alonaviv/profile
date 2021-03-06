# Generated by Django 3.1.2 on 2020-12-29 12:13

from django.db import migrations, models
import profile_server.pronouns


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_teacheruser_pronoun_choice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacheruser',
            name='pronoun_choice',
            field=models.CharField(choices=[(profile_server.pronouns.PronounOptions['MALE'], 'לשון זכר'), (profile_server.pronouns.PronounOptions['FEMALE'], 'לשון נקבה'), (profile_server.pronouns.PronounOptions['NEUTRAL'], 'לשון ניטרלית'), (profile_server.pronouns.PronounOptions['MIXED'], 'לשון מעורבבת')], max_length=10),
        ),
    ]
