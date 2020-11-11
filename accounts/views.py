from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect, HttpResponse

from accounts.forms import RegisterForm, LoginForm
from evaluations.models import Teacher
from evaluations.views import main_evaluations_page


def get_username(first_name, last_name):
    return f"{first_name}_{last_name}"


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = get_username(form.cleaned_data['first_name'], form.cleaned_data['last_name'])
            try:
                user = User.objects.create_user(username=username,
                                                email=form.cleaned_data['email'],
                                                password=form.cleaned_data['password'],
                                                first_name=form.cleaned_data['first_name'],
                                                last_name=form.cleaned_data['last_name'])
            except IntegrityError:
                messages.error(request, "User already exists")

            else:
                Teacher.objects.get_or_create(first_name=form.cleaned_data['first_name'],
                                              last_name=form.cleaned_data['last_name'],
                                              email=form.cleaned_data['email'],
                                              is_homeroom_teacher=form.cleaned_data['is_homeroom_teacher'],
                                              house=form.cleaned_data['house'],
                                              user=user)

                auth.authenticate(username=username, password=form.cleaned_data['password'])
                auth.login(request, user)

                return redirect(main_evaluations_page)

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
                return redirect(main_evaluations_page)
            else:
                messages.error(request, "Wrong Credentials")

    else:
        form = LoginForm()

    context = {'form': form}
    return render(request, "accounts/login.html", context)


def logout(request):
    auth.logout(request)
    return redirect(main_evaluations_page)


