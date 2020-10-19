from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_evaluations_page),
    path('write', views.write_evaluations),
    path('read', views.read_evaluations)
]
