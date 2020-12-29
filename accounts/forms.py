from django.forms import Form, CharField, EmailField, BooleanField, ModelChoiceField, PasswordInput, ChoiceField

from evaluations.models import House
from profile_server.pronouns import PronounOptions


class RegisterForm(Form):
    first_name = CharField(label='שם פרטי')
    last_name = CharField(label='שם משפחה')
    pronoun_choice = ChoiceField(choices=[('', '---------')] + [(pronoun_option.name, pronoun_option.value)
                                                                for pronoun_option in PronounOptions],
                                 label='לשון פנייה')
    is_homeroom_teacher = BooleanField(required=False, label='האם חונכ/ת?')
    house = ModelChoiceField(House.objects.all(), label="שכבה")
    email = EmailField(label="אימייל")
    password = CharField(widget=PasswordInput(), label='סיסמא')
    confirm_password = CharField(widget=PasswordInput(), label='וידוא סיסמא')


class LoginForm(Form):
    first_name = CharField(label='שם פרטי')
    last_name = CharField(label='שם משפחה')
    password = CharField(widget=PasswordInput(), label='סיסמא')
