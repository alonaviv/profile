from django.shortcuts import render
from .models import Evaluation, Student


def main_evaluations_page(request):
    return render(request, 'evaluations/index.html')


def write_evaluations(request):
    return render(request, 'evaluations/write_evaluation.html')


def read_evaluations(request):
    teacher_first_name = 'שני'
    teacher_last_name = 'ורמן'

    students = Student.objects.filter(homeroom_teacher__first_name=teacher_first_name,
                                      homeroom_teacher__last_name=teacher_last_name).order_by('first_name',
                                                                                              'last_name')
    evaluations_by_student = {}
    for student in students:
        evaluations_by_student[student] = Evaluation.objects.filter(student=student).order_by('evaluated_class__name')

    context = {'evaluations_by_student': evaluations_by_student}

    return render(request, 'evaluations/read_evaluation.html', context)

