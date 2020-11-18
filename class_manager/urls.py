from django.urls import path
from . import views

urlpatterns = [
    # Manage Classes
    path('manage_classes', views.manage_classes, name='manage_classes'),
    path('manage_students_in_class/<int:class_id>', views.manage_students_in_class, name='manage_students_in_class'),
    path('add_new_class', views.add_new_class, name='add_new_class'),
    path('edit_class_data/<int:class_id>', views.edit_class_data, name='edit_class_data'),
    path('add_students_to_class/<int:class_id>/<int:house_id>', views.add_students_to_class, name='add_students_to_class'),
    path('add_students_to_class/<int:class_id>', views.add_students_to_class, name='add_students_to_class'),
    path('delete_student_from_class/<int:class_id>/<int:student_id>', views.delete_student_from_class, name='delete_student_from_class'),
    path('delete_class/<int:class_id>', views.delete_class, name='delete_class'),

    # Manage Homeroom
    path('manage_homeroom', views.manage_homeroom, name='manage_homeroom'),
    path('add_students_to_homeroom/<int:house_id>', views.add_students_to_homeroom, name='add_students_to_homeroom'),
    path('add_students_to_homeroom', views.add_students_to_homeroom, name='add_students_to_homeroom'),
    path('delete_student_from_homeroom/<int:student_id>', views.delete_student_from_homeroom, name='delete_student_from_homeroom'),
] 