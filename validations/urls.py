from django.urls import path
from . import views

urlpatterns = [
    path('', views.validations_summary, name='validations_summary')
]
