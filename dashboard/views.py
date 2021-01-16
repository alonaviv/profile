from django.shortcuts import render

from evaluations.models import Student
from evaluations.views import populate_evaluations_in_teachers_classes
from utils.school_dates import get_current_trimester


def ssl(request):
    from django.http import HttpResponse
    text = "DCBAB19E72D56A4368CE6355380BCE6FA3508DF993D3DBB452D1CA643C7093C4 comodoca.com 6002a68a39573"

    return HttpResponse(text, content_type='text/plain')


def main_dashboard_page(request):
    teacher = request.user
    populate_evaluations_in_teachers_classes(teacher)

    context = get_dashboard_context(teacher)

    return render(request, 'dashboard/dashboard.html', context)


def get_dashboard_context(teacher):
    if teacher and not teacher.is_anonymous:
        classes = teacher.class_set.filter(hebrew_year=get_current_trimester().hebrew_school_year)
        homeroom_students = teacher.student_set.all()

        # Get's all the students that the teacher teaches, without duplicates
        class_students = Student.objects.none()
        for klass in classes:
            class_students |= klass.students.all()

        class_students = class_students.distinct()

        teachers_missing_evaluations = {}
        for missing_evals in teacher.missing_evals_of_homeroom_students_in_current_trimester:
            lazy_teacher = missing_evals.evaluated_class.teacher
            teachers_missing_evaluations[str(lazy_teacher)] = teachers_missing_evaluations.get(str(lazy_teacher), 0) + 1

        homeroom_students_without_classes = homeroom_students.filter(classes__isnull=True)

    else:
        classes = []
        class_students = []
        homeroom_students = []
        teachers_missing_evaluations = {}
        homeroom_students_without_classes = []
    context = {
        'classes': classes, 'teacher': teacher, 'class_students': class_students,
        'homeroom_students': homeroom_students, 'teachers_missing_evaluations': teachers_missing_evaluations,
        'homeroom_students_without_classes': homeroom_students_without_classes
    }
    return context
