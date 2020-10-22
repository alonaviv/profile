from django.forms import Form, CharField, EmailField, BooleanField, ModelChoiceField, PasswordInput
from django.contrib.auth.models import User
from evaluations.models import House


# TODO: Validate password and email twice
class RegisterForm(Form):
    first_name = CharField()
    last_name = CharField()
    is_homeroom_teacher = BooleanField(required=False)
    house = ModelChoiceField(House.objects.all())
    email = EmailField()
    password = CharField(widget=PasswordInput())


class LoginForm(Form):
    first_name = CharField()
    last_name = CharField()
    password = CharField(widget=PasswordInput())
