from django.urls import path

from . import views

urlpatterns = [
    path('write_evaluations', views.write_evaluations_main_page, name='write'),
    path('write_evaluations/<int:class_id>', views.write_class_evaluations, name='write_class_evaluations'),
    path('write_evaluations/<int:class_id>/<str:anchor>', views.write_class_evaluations,
         name='write_class_evaluations_with_anchor'),
    path('view_evaluations', views.view_evaluations_main_page, name='view'),
    path('view_evaluations/<int:student_id>', views.view_student_evaluations, name='view_student_evaluations'),
    path('view_evaluations/<int:student_id>/download', views.download_student_evaluations,
         name='download_student_evaluations'),
    path('evaluation_details/<int:student_id>', views.evaluations_details, name='evaluation_details'),
    path('remove_evaluation/<int:evaluation_id>', views.remove_evaluation, name='remove_evaluation'),
    path('display_single_eval/<int:evaluation_id>', views.view_single_eval, name='view_single_eval')
]
