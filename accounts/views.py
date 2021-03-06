from django.contrib import auth, messages
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetConfirmView
from django.db import IntegrityError
from django.forms import ValidationError
from django.shortcuts import render, redirect, reverse
from django_email_verification import sendConfirm

from accounts.forms import RegisterForm, LoginForm, MySetPasswordForm
from emails.send_emails import send_forgot_password_email
from evaluations.models import Teacher
from profile_server.pronouns import PronounWordDictionary

TeacherUser = get_user_model()


def resend_confirmation_email(request, user_id):
    try:
        user = TeacherUser.objects.get(id=user_id)
    except TeacherUser.DoesNotExist:
        return render(request, 'common/general_error_page.html',
                      {'error_message': 'לא ניתן לשלוח מייל אישור הרשמה - המשתמש המבוקש אינו נמצא במערכת'})

    sendConfirm(user)
    return render(request, 'accounts/sent_verification_email.html', context={'new_user': user})


def get_username(first_name, last_name):
    username_with_spaces = first_name + ' ' + last_name
    username_without_spaces = username_with_spaces.replace(' ', '_')
    username_with_valid_chars = ''.join(c for c in username_without_spaces if c.isalnum() or c == '_')

    return username_with_valid_chars


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            try:
                teacher_object = Teacher.objects.get(first_name=first_name, last_name=last_name)
            except Teacher.DoesNotExist:
                messages.error(request, f"המורה {first_name} {last_name} לא רשומ/ה במאגר בית הספר")
                return render(request, "accounts/register.html", {'form': form})

            try:
                password_validation.validate_password(form.cleaned_data['password'])
            except ValidationError:
                messages.error(request,
                               "הסיסמא צריכה להכיל אותיות באנגלית ומספרים ביחד, ולהיות באורך של 8 תווים לפחות")
                return render(request, "accounts/register.html", {'form': form})

            if form.cleaned_data['password'] != form.cleaned_data['confirm_password']:
                messages.error(request, "הסיסמאות אינן תואמות זו לזו")
                return render(request, "accounts/register.html", {'form': form})

            username = get_username(first_name, last_name)

            # If a user isn't verified yet (didn't click the email link), we give them a chance to register
            # again, with a different email for instance.
            try:
                non_verified_user = TeacherUser.objects.get(username=username, is_active=False)
            except TeacherUser.DoesNotExist:
                class EmptyUser:
                    @property
                    def email(self):
                        return ''

                    def __bool__(self):
                        return False

                non_verified_user = EmptyUser()

            if TeacherUser.objects.filter(email=form.cleaned_data['email']).exclude(
                    email=non_verified_user.email).exists():
                messages.error(request, "קיים כבר משתמש עם כתובת המייל הזו")
                return render(request, "accounts/register.html", {'form': form})

            if non_verified_user:
                non_verified_user.delete()

            try:
                user = TeacherUser.objects.create_user(username=username,
                                                       email=form.cleaned_data['email'],
                                                       password=form.cleaned_data['password'],
                                                       pronoun_choice=form.cleaned_data['pronoun_choice'],
                                                       first_name=first_name,
                                                       last_name=last_name,
                                                       house=form.cleaned_data['house'],
                                                       is_homeroom_teacher=form.cleaned_data['is_homeroom_teacher'],
                                                       teacher_object=teacher_object)

                sendConfirm(user)
                return render(request, 'accounts/sent_verification_email.html', context={'new_user': user})

            except (IntegrityError, ValidationError):
                messages.error(request, f"המשתמש/ת {teacher_object} כבר קיימ/ת במערכת")

    else:
        form = RegisterForm()

    context = {'form': form}
    return render(request, "accounts/register.html", context)


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = get_username(form.cleaned_data['first_name'], form.cleaned_data['last_name'])
            user = auth.authenticate(username=username, password=form.cleaned_data['password'])

            if user is not None:
                auth.login(request, user)
                return redirect(reverse('index'))
            else:
                try:
                    user = TeacherUser.objects.get(username=username)
                    if user.is_active:
                        messages.error(request, "הסיסמא אינה נכונה")
                    else:
                        messages.error(request, "טרם אישרת את הרישום (באמצעות הלינק במייל)")

                except TeacherUser.DoesNotExist:
                    messages.error(request, "טרם נרשמת במערכת")

    else:
        form = LoginForm()

    context = {'form': form}
    return render(request, "accounts/login.html", context)


def logout(request):
    auth.logout(request)
    return redirect(reverse('index'))


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        password_reset_form.fields['email'].label = 'כתובת אימייל'

        if password_reset_form.is_valid():
            requested_email = password_reset_form.cleaned_data['email']

            try:
                user = TeacherUser.objects.get(email=requested_email)
            except TeacherUser.DoesNotExist:
                messages.error(request, "כתובת המייל אינה תואמת למשתמש קיים במערכת")
                return render(request=request, template_name="accounts/password_reset.html",
                              context={"password_reset_form": password_reset_form})

            send_forgot_password_email(user)

            pronoun_dict = PronounWordDictionary(user.pronoun_as_enum)
            messages.info(request,
                          f"המייל נשלח {pronoun_dict['to_you']}. אם הוא לא נמצא, {pronoun_dict['look']} בתיקיית הספאם. ")

    else:
        password_reset_form = PasswordResetForm()
        password_reset_form.fields['email'].label = 'כתובת אימייל'

    return render(request=request, template_name="accounts/password_reset.html",
                  context={"password_reset_form": password_reset_form})


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = MySetPasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['pronoun_dict'] = PronounWordDictionary(self.user.pronoun_as_enum)

        return context
