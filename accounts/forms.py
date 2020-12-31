from django.forms import Form, CharField, EmailField, BooleanField, ModelChoiceField, PasswordInput, ChoiceField
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from django.contrib import messages


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


# My own version of auth.forms.SetPasswordForm
class MySetPasswordForm(Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': 'הסיסמאות אינן תואמות זו לזו'
    }
    new_password1 = CharField(
        label="סיסמא חדשה",
        widget=PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )
    new_password2 = CharField(
        label="וידוא סיסמא",
        strip=False,
        widget=PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
