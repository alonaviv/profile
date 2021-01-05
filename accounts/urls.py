from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('teacher_login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('reset/<uidb64>/<token>/',
         views.MyPasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),
    path('resend_confirmation_email/<int:user_id>', views.resend_confirmation_email, name='resend_confirmation_email')
]
