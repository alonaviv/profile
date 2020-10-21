from django.forms import inlineformset_factory, HiddenInput
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from .models import Teacher, Evaluation, Class

TRIMESTER = 1
TEACHER_FIRST_NAME = 'שני'
TEACHER_LAST_NAME = 'ורמן'


def main_evaluations_page(request):
    return render(request, 'evaluations/index.html')


def _populate_evaluations(teacher):
    """
    Make sure that there is an evaluation object in the DB for each student in each class of the given teacher.
    If there isn't, create an entry with empty text.
    """
    for evaluated_class in teacher.class_set.all():
        for student in evaluated_class.student_set.all():
            try:
                Evaluation.objects.get(student=student, evaluated_class=evaluated_class)
            except Evaluation.DoesNotExist:
                Evaluation.objects.create(student=student, evaluated_class=evaluated_class, trimester=TRIMESTER)


def write_class_evaluations(request, class_id):
    teacher = Teacher.objects.get(first_name=TEACHER_FIRST_NAME, last_name=TEACHER_LAST_NAME)

    try:
        class_to_evaluate = Class.objects.get(id=class_id, teacher=teacher)
    except Class.DoesNotExist:
        return HttpResponseBadRequest("<h1> Wrong class selection for teacher </h1>")

    EvaluationFormSet = inlineformset_factory(Class,
                                              Evaluation,
                                              fields=['evaluation_text', 'student'],
                                              widgets={'student': HiddenInput()},
                                              extra=0,
                                              can_delete=False)
    classes = teacher.class_set.all()

    if request.method == 'POST':
        formset = EvaluationFormSet(request.POST, instance=class_to_evaluate)
        formset.save()

    else:
        formset = EvaluationFormSet(instance=class_to_evaluate)

    context = {'classes': classes, 'formset': formset, 'trimester': 1}
    return render(request, 'evaluations/write_evaluations.html', context)


def write_evaluations_main_page(request):
    teacher = Teacher.objects.get(first_name=TEACHER_FIRST_NAME, last_name=TEACHER_LAST_NAME)
    _populate_evaluations(teacher)

    from django.http import HttpResponse
    return HttpResponse("<h1> Write Evaluations </h1>")


def view_evaluations(request):
    teacher = Teacher.objects.get(first_name=TEACHER_FIRST_NAME, last_name=TEACHER_LAST_NAME)
    students = teacher.student_set.all()

    context = {'students': students}
    return render(request, 'evaluations/view_evaluations.html', context)
