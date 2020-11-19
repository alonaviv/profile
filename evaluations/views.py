from django.forms import inlineformset_factory, HiddenInput, Textarea
from django.http import HttpResponseBadRequest
from django.shortcuts import render, reverse, redirect
from django.contrib.auth.decorators import login_required

from .models import Teacher, Evaluation, Class, Student, StudentNotInClassError

TRIMESTER = 1

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
    for evaluated_class in teacher.class_set.all():
        for student in evaluated_class.students.all():
            try:
                Evaluation.objects.get(student=student, evaluated_class=evaluated_class)
            except Evaluation.DoesNotExist:
                evaluation = Evaluation(student=student, evaluated_class=evaluated_class, trimester=TRIMESTER)
                evaluation.clean()
                evaluation.save()

    for evaluation in Evaluation.objects.all():
        try:
            evaluation.clean()
        except StudentNotInClassError:
            evaluation.delete()


@login_required
def write_class_evaluations(request, class_id):
    teacher = request.user
    try:
        class_to_evaluate = Class.objects.get(id=class_id, teacher=teacher)
    except Class.DoesNotExist:
        return HttpResponseBadRequest("<h1> Wrong class selection for teacher </h1>")

    EvaluationFormSet = inlineformset_factory(Class,
                                              Evaluation,
                                              fields=['evaluation_text', 'student'],
                                              widgets={
                                                  'student': HiddenInput(),
                                                  'evaluation_text': Textarea(attrs={'rows': 20, 'cols': 60}),
                                              },
                                              extra=0,
                                              can_delete=False)
    classes = teacher.class_set.all()

    if request.method == 'POST':
        formset = EvaluationFormSet(request.POST, instance=class_to_evaluate)
        formset.save()

    else:
        formset = EvaluationFormSet(instance=class_to_evaluate)

    context = {'classes': classes, 'formset': formset, 'trimester': 1, 'teacher': teacher}
    return render(request, 'evaluations/write_evaluations.html', context)


@login_required
def write_evaluations_main_page(request):
    teacher = request.user

    if teacher:
        classes = teacher.class_set.all()
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

    if not teacher.is_homeroom_teacher:
        return redirect(reverse('not_homeroom_teacher_error'))

    student = Student.objects.get(id=student_id)

    missing_classes = []

    for evaluation in student.evaluation_set.all():
        if not evaluation.evaluation_text:
            missing_classes.append(evaluation.evaluated_class)

    context = {'student': student, 'missing_classes': missing_classes, 'teacher': teacher}
    return render(request, 'evaluations/missing_evaluations.html', context)


def failed_login(request):
    return render(request, 'evaluations/failed_login.html')
