from django.forms import Form, CharField, EmailField, BooleanField, ModelChoiceField, PasswordInput, ValidationError
from django.core.validators import EmailValidator
from evaluations.models import House


class RegisterForm(Form):
    first_name = CharField(label='שם פרטי')
    last_name = CharField(label='שם משפחה')
    is_homeroom_teacher = BooleanField(required=False, label='האם חונכ/ת?')
    house = ModelChoiceField(House.objects.all(), label="שכבה")
    email = EmailField(label="אימייל")
    password = CharField(widget=PasswordInput(), label='סיסמא')
    confirm_password = CharField(widget=PasswordInput(), label='וידוא סיסמא')


class LoginForm(Form):
    first_name = CharField(label='שם פרטי')
    last_name = CharField(label='שם משפחה')
    password = CharField(widget=PasswordInput(), label='סיסמא')
