from django.contrib import auth, messages
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.db import IntegrityError
from django.db.models.query_utils import Q
from django.forms import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from profile_server.settings import EMAIL_HOST_USER

from accounts.forms import RegisterForm, LoginForm
from evaluations.models import Teacher

TeacherUser = get_user_model()


def get_username(first_name, last_name):
    return f"{first_name}_{last_name}"


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
                               "הסיסמא צריכה להכיל אותיות ומספרים, להיות באורך של 8 תווים לפחות, ולא להיות דומה מדי לשם שלך")
                return render(request, "accounts/register.html", {'form': form})

            if form.cleaned_data['password'] != form.cleaned_data['confirm_password']:
                messages.error(request, "הסיסמאות אינן תואמות")
                return render(request, "accounts/register.html", {'form': form})

            if TeacherUser.objects.filter(email=form.cleaned_data['email']).exists():
                messages.error(request, "קיים כבר משתמש עם כתובת המייל הזו")
                return render(request, "accounts/register.html", {'form': form})

            username = get_username(first_name, last_name)
            try:
                user = TeacherUser.objects.create_user(username=username,
                                                       email=form.cleaned_data['email'],
                                                       password=form.cleaned_data['password'],
                                                       first_name=first_name,
                                                       last_name=last_name,
                                                       house=form.cleaned_data['house'],
                                                       is_homeroom_teacher=form.cleaned_data['is_homeroom_teacher'],
                                                       teacher_object=teacher_object)

                auth.authenticate(username=username, password=form.cleaned_data['password'])
                auth.login(request, user)

                return redirect(reverse('index'))

            except IntegrityError as e:
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
                messages.error(request, "פרטי הכניסה אינם נכונים (או שטרם נרשמת במערכת)")

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
        if password_reset_form.is_valid():
            requested_email = password_reset_form.cleaned_data['email']

            try:
                user = TeacherUser.objects.get(email=requested_email)
            except TeacherUser.DoesNotExist:
                messages.error(request, "כתובת המייל אינה תואמת למשתמש קיים במערכת")
                return render(request=request, template_name="accounts/password_reset.html",
                              context={"password_reset_form": password_reset_form})

            subject = "Password Reset Requested"
            email_template_name = "accounts/password_reset_email.txt"
            context = {
                "email": user.email,
                'domain': '127.0.0.1:8000',
                'site_name': 'Website',
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                'token': default_token_generator.make_token(user),
                'protocol': 'http',
            }
            email = render_to_string(email_template_name, context)
            try:
                send_mail(subject, email, EMAIL_HOST_USER, [user.email], fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect(reverse('password_reset_done'))

    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="accounts/password_reset.html",
                  context={"password_reset_form": password_reset_form})
