from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_evaluations_page, name='index'),
    path('write_evaluations', views.write_evaluations_main_page, name='write'),
    path('write_evaluations/<int:class_id>', views.write_class_evaluations, name='write_class_evaluations'),
    path('view_evaluations', views.view_evaluations_main_page, name='view'),
    path('view_evaluations/<int:student_id>', views.view_student_evaluations, name='view_student_evaluations'),
    path('missing_evaluations/<int:student_id>', views.missing_evaluations, name='missing_student_evaluations'),
]
