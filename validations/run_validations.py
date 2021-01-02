"""
All validations return a tuple of (validation_result_boolean, data) - False means that bad data exists.
These functions should be called each time anyone needs this data, so it's fresh data always.
"""

from evaluations.models import Student, Teacher
from django.db.models import Count
from profile_config import MIN_AMOUNT_OF_CLASSES


def validate_all_students_have_homerooms():
    students_without_homerooms = Student.objects.filter(homeroom_teacher=None)
    return len(students_without_homerooms) == 0, students_without_homerooms


def validate_all_students_have_valid_homeroom_teachers():
    """
    Finds students who's homeroom teacher object isn't actually a homeroom teacher
    """
    students_without_valid_homeroom_teachers = Student.objects.filter(homeroom_teacher__is_homeroom_teacher=False)
    return len(students_without_valid_homeroom_teachers) == 0, students_without_valid_homeroom_teachers


def validate_all_teachers_have_registered():
    unregistered_teachers = Teacher.objects.filter(teacheruser=None)
    return len(unregistered_teachers) == 0, unregistered_teachers


def validate_all_students_have_classes():
    students_without_classes = Student.objects.filter(classes=None)
    return len(students_without_classes) == 0, students_without_classes


def validate_all_students_have_minimal_amount_of_classes(min_num_classes=MIN_AMOUNT_OF_CLASSES):
    """
    Returns a 3 value tuple: (result boolean, students with few classes, the minimal amount of classes for students)
    """
    students_with_few_num_of_classes = Student.objects.annotate(num_classes=Count('classes')).filter(
        num_classes__lt=min_num_classes)
    return len(students_with_few_num_of_classes) == 0, students_with_few_num_of_classes, min_num_classes
