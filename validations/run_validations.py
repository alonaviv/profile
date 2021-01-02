"""
These functions should be called each time anyone needs this data, so it's fresh data always.
"""
from dataclasses import dataclass
from typing import Type
from evaluations.models import Student, Teacher
from django.db.models import Count
from django.db.models import QuerySet
from profile_config import MIN_AMOUNT_OF_CLASSES
from functools import wraps


all_validations = []
urgent_validations = []


def validation(func):
    all_validations.append(func)

    @wraps(func)
    def add_to_validations():
        return func()

    return add_to_validations


def urgent_validation(func):
    all_validations.append(func)
    urgent_validations.append(func)

    @wraps(func)
    def add_to_urgent_validations():
        return func()

    return add_to_urgent_validations


@dataclass
class ValidationResult:
    failed_objects: Type[QuerySet]
    success_validation_title: str
    failure_validation_title_format: str  # String using the formal variable { num_failed_objects }
    failure_validation_item_format: str  # String using the formal variable { failed_object }

    @property
    def bool_result(self):
        return len(self.failed_objects) == 0

    @property
    def failed_validation_title(self):
        return self.failure_validation_title_format.format(num_failed_objects=len(self.failed_objects))

    @property
    def failed_items_messages(self):
        for failed_object in self.failed_objects:
            yield self.failure_validation_item_format.format(failed_object=failed_object)


@urgent_validation
def validate_all_students_have_homerooms():
    students_without_homerooms = Student.objects.filter(homeroom_teacher=None)
    return ValidationResult(
        failed_objects=students_without_homerooms,
        success_validation_title="כל התלמידים בבית הספר משוייכים לחונכים",
        failure_validation_title_format="{num_failed_objects} תלמידים אינם משוייכים לחונכ/ת:",
        failure_validation_item_format="{failed_object}"
    )


@urgent_validation
def validate_all_students_have_valid_homeroom_teachers():
    """
    Finds students who's homeroom teacher object isn't actually a homeroom teacher
    """
    students_without_valid_homeroom_teachers = Student.objects.filter(homeroom_teacher__is_homeroom_teacher=False)
    return ValidationResult(
        failed_objects=students_without_valid_homeroom_teachers,
        success_validation_title="כל המורים אליהם משוייכים תלמידים בבית הספר רשומים כחונכים",
        failure_validation_title_format="{num_failed_objects} תלמידים משוייכים למורה שאינו/שאינה חונכ/ת:",
        failure_validation_item_format="{{failed_object}} - {{failed_object.homeroom_teacher}}}"
    )


@urgent_validation
def validate_all_teachers_have_registered():
    unregistered_teachers = Teacher.objects.filter(teacheruser=None)

    return ValidationResult(
        failed_objects=unregistered_teachers,
        success_validation_title="כל המורים השמורים במאגר נרשמו בהצלחה למערכת",
        failure_validation_title_format="{num_failed_objects} מורים לא רשומים למערכת:",
        failure_validation_item_format="{failed_object}"
    )


@validation
def validate_all_students_have_classes():
    students_without_classes = Student.objects.filter(classes=None)

    return ValidationResult(
        failed_objects=students_without_classes,
        success_validation_title="כל התלמידים בבית הספר רשומים לשיעורים",
        failure_validation_title_format="{num_failed_objects} תלמידים לא רשומים לאף שיעור:",
        failure_validation_item_format="{failed_object}"
    )


@validation
def validate_all_students_have_minimal_amount_of_classes():
    """
    Returns a 3 value tuple: (result boolean, students with few classes, the minimal amount of classes for students)
    """
    students_with_few_num_of_classes = Student.objects.annotate(num_classes_annotation=Count('classes')).filter(
        num_classes_annotation__lt=MIN_AMOUNT_OF_CLASSES)
    return ValidationResult(
        failed_objects=students_with_few_num_of_classes,
        success_validation_title=f"כל התלמידים בבית הספר רשומים ללפחות {MIN_AMOUNT_OF_CLASSES} שיעורים",
        failure_validation_title_format=f"{{num_failed_objects}} תלמידים רשומים לפחות מ-{MIN_AMOUNT_OF_CLASSES} שיעורים",
        failure_validation_item_format="{failed_object} - {failed_object.num_classes} שיעורים"
    )
