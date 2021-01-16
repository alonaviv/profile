"""profile_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView, TemplateView
from django_email_verification import urls as email_verification_urls

from dashboard.views import ssl
urlpatterns = [
    path('.well-known/pki-validation/7433A6D5F501B1147F258DCD5990FE61.txt', ssl),
    path('', RedirectView.as_view(url='/dashboard'), name='index'),
    path('dashboard', include('dashboard.urls')),
    path('evaluations/', include('evaluations.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
    path('email/', include('emails.urls')),
    path('class_manager/', include('class_manager.urls')),
    path('validations/', include('validations.urls')),
    path('registration_verification/', include(email_verification_urls)),
    path('failed_login', TemplateView.as_view(template_name='common/failed_login.html'), name='failed_login'),
    path('not_homeroom_teacher_error', TemplateView.as_view(template_name='common/not_homeroom_teacher_error.html'),
         name='not_homeroom_teacher_error'),
    path('mismatched_homeroom_teacher_error',
         TemplateView.as_view(template_name='common/mismatched_homeroom_teacher_error.html'),
         name='mismatched_homeroom_teacher_error'),
    path('mismatched_professional_teacher_error',
         TemplateView.as_view(template_name='common/mismatched_professional_teacher_error.html'),
         name='mismatched_professional_teacher_error'),
]
