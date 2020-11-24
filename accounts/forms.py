from django.forms import Form, CharField, EmailField, BooleanField, ModelChoiceField, PasswordInput, ValidationError

from evaluations.models import House


class RegisterForm(Form):
    first_name = CharField(label='שם פרטי')
    last_name = CharField(label='שם משפחה')
    is_homeroom_teacher = BooleanField(required=False, label='?האם חונכ/ת')
    house = ModelChoiceField(House.objects.all(), label="שכבה", required=False)
    email = EmailField(label="אימייל")
    password = CharField(widget=PasswordInput(), label='סיסמא')
    confirm_password = CharField(widget=PasswordInput(), label='אישור סיסמא')

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['password'] != cleaned_data['confirm_password']:
            raise ValidationError("הסיסמאות שהכנסת אינן תואמות")

        if cleaned_data['is_homeroom_teacher']:
            if cleaned_data['house'] is None:
                raise ValidationError("לא ניתן להרשם כחונכ/ת מבלי לבחור שכבה")

        return cleaned_data


class LoginForm(Form):
    first_name = CharField(label='שם פרטי')
    last_name = CharField(label='שם משפחה')
    password = CharField(widget=PasswordInput(), label='סיסמא')
