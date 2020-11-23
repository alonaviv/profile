from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory, Textarea
from django.http import HttpResponseBadRequest
from django.shortcuts import render, reverse, redirect
from utils.school_dates import get_current_trimester_and_hebrew_year

from .models import Evaluation, Class, Student, StudentNotInClassError

"""
Every view in the site needs to pass the teacher object in the context, so it can display the name
of the logged in teacher in the navbar. Note that teacher in this context is the TeacherUser, not the Teacher object which is used to verify that the user is expected.
"""


def main_evaluations_page(request):
    context = {'teacher': request.user}
    return render(request, 'evaluations/index.html', context)


def populate_evaluations_in_teachers_classes(teacher):
    """
    Make sure that there is an evaluation object in the DB for each student in each class of the given teacher.
    If there isn't, create an entry with empty text. Delete all evaluations where the student isn't in the class. 
    """
    current_trimester, current_hebrew_year = get_current_trimester_and_hebrew_year()

    for evaluated_class in teacher.class_set.filter(hebrew_year=current_hebrew_year):
        for student in evaluated_class.students.all():
            try:
                Evaluation.objects.get(student=student, evaluated_class=evaluated_class,
                                       hebrew_year=current_hebrew_year, trimester=current_trimester)
            except Evaluation.DoesNotExist:
                current_trimester, current_hebrew_year = get_current_trimester_and_hebrew_year()
                evaluation = Evaluation(student=student, evaluated_class=evaluated_class,
                                        trimester=current_trimester, hebrew_year=current_hebrew_year)
                evaluation.clean()
                evaluation.save()

    # TODO: Figure this part out. Is the filter correct?
    for evaluation in Evaluation.objects.filter(hebrew_year=current_hebrew_year, trimester=current_trimester):
        try:
            evaluation.clean()
        except StudentNotInClassError:
            evaluation.delete()


@login_required
def write_class_evaluations(request, class_id):
    current_trimester, current_hebrew_year = get_current_trimester_and_hebrew_year()

    teacher = request.user
    try:
        class_to_evaluate = Class.objects.get(id=class_id, teacher=teacher, hebrew_year=current_hebrew_year)
    except Class.DoesNotExist:
        return HttpResponseBadRequest("<h1> Wrong class selection for teacher </h1>")

    EvaluationFormSet = inlineformset_factory(Class,
                                              Evaluation,
                                              fields=['evaluation_text'],
                                              widgets={
                                                  'evaluation_text': Textarea(attrs={'rows': 20, 'cols': 60}),
                                              },
                                              extra=0,
                                              can_delete=False)

    if request.method == 'POST':
        formset = EvaluationFormSet(request.POST, instance=class_to_evaluate,
                                    queryset=Evaluation.objects.filter(hebrew_year=current_hebrew_year,
                                                                       trimester=current_trimester))
        formset.save()

    else:
        formset = EvaluationFormSet(instance=class_to_evaluate,
                                    queryset=Evaluation.objects.filter(hebrew_year=current_hebrew_year,
                                                                       trimester=current_trimester))

    context = {'formset': formset, 'teacher': teacher}
    return render(request, 'evaluations/write_evaluations.html', context)


@login_required
def write_evaluations_main_page(request):
    current_trimester, current_year = get_current_trimester_and_hebrew_year()
    teacher = request.user

    populate_evaluations_in_teachers_classes(teacher)

    if teacher:
        classes = teacher.class_set.filter(hebrew_year=current_year)
    else:
        classes = []

    context = {'classes': classes, 'teacher': teacher}
    return render(request, 'evaluations/write_evaluations_index.html', context)


@login_required
def view_student_evaluations(request, student_id):
    teacher = request.user

    if not teacher.is_homeroom_teacher:
        return redirect(reverse('not_homeroom_teacher_error'))

    student = Student.objects.get(id=student_id)
    context = {'student': student, 'teacher': teacher}
    return render(request, 'evaluations/view_evaluations.html', context)


@login_required
def view_evaluations_main_page(request):
    teacher = request.user

    if not teacher.is_homeroom_teacher:
        return redirect(reverse('not_homeroom_teacher_error'))

    if teacher:
        students = teacher.student_set.all()
    else:
        students = []

    context = {'students': students, 'teacher': teacher}
    return render(request, 'evaluations/view_evaluations_index.html', context)


@login_required
def missing_evaluations(request, student_id):
    teacher = request.user
    current_trimester, current_year = get_current_trimester_and_hebrew_year()

    if not teacher.is_homeroom_teacher:
        return redirect(reverse('not_homeroom_teacher_error'))

    student = Student.objects.get(id=student_id)

    missing_classes = []

    for evaluation in student.evaluation_set.filter(trimester=current_trimester, hebrew_year=current_year):
        if not evaluation.evaluation_text:
            missing_classes.append(evaluation.evaluated_class)

    context = {'student': student, 'missing_classes': missing_classes, 'teacher': teacher}
    return render(request, 'evaluations/missing_evaluations.html', context)


def failed_login(request):
    return render(request, 'evaluations/failed_login.html')
