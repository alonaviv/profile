from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_evaluations_page, name='index'),
    path('write_evaluations', views.write_evaluations_main_page, name='write'),
    path('write_evaluations/<int:class_id>', views.write_class_evaluations, name='write_class_evaluations'),
    path('view_evaluations', views.view_evaluations, name='view'),
    path('failed_login', views.failed_login, name='failed_login')
]
