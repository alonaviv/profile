from django.contrib import auth, messages
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import render, redirect, reverse

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

            except IntegrityError:
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
                messages.error(request, "Wrong Credentials")

    else:
        form = LoginForm()

    context = {'form': form}
    return render(request, "accounts/login.html", context)


def logout(request):
    auth.logout(request)
    return redirect(reverse('index'))


