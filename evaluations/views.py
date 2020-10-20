from django.shortcuts import render
from .models import Teacher, Evaluation
from .forms import EvaluationForm, EvaluationFormSet


def main_evaluations_page(request):
    return render(request, 'evaluations/index.html')


def _populate_evaluations(class_to_evaluate, trimester):
    """
    Make sure that there is an evaluation object in the DB for each student in each class of the given teacher.
    If there isn't, create an entry with empty text.
    The forms will then be populated from all existing entries, whether with text or not.
    """
    for student in class_to_evaluate.student_set.all():
        try:
            Evaluation.objects.get(student=student, evaluated_class=evaluated_class)
        except Evaluation.DoesNotExist:
            Evaluation.objects.create(student=student, evaluated_class=evaluated_class, trimester=trimester)


def write_evaluations(request):
    teacher_first_name = 'שני'
    teacher_last_name = 'ורמן'
    teacher = Teacher.objects.get(first_name=teacher_first_name, last_name=teacher_last_name)
    _populate_evaluations(teacher, 1)
    classes = teacher.class_set.all()

    if request.method == 'POST':
        formset = EvaluationFormSet(request.POST)
        #breakpoint()

        formset.save()

    else:
        formset = EvaluationFormSet()

    context = {'classes': classes, 'formset': formset, 'trimester': 1}
    return render(request, 'evaluations/write_evaluation.html', context)


def read_evaluations(request):
    teacher_first_name = 'שני'
    teacher_last_name = 'ורמן'
    teacher = Teacher.objects.get(first_name=teacher_first_name, last_name=teacher_last_name)
    students = teacher.student_set.all()

    context = {'students': students}
    return render(request, 'evaluations/read_evaluation.html', context)

