from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory, Textarea
from django.shortcuts import render, reverse, redirect

from utils.school_dates import get_current_trimester
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
    if not teacher.is_anonymous:
        current_trimester = get_current_trimester()

        for evaluated_class in teacher.class_set.filter(hebrew_year=current_trimester.hebrew_school_year):
            for student in evaluated_class.students.all():
                try:
                    Evaluation.objects.get(student=student, evaluated_class=evaluated_class,
                                           hebrew_year=current_trimester.hebrew_school_year,
                                           trimester=current_trimester.name)
                except Evaluation.DoesNotExist:
                    current_trimester = get_current_trimester()
                    evaluation = Evaluation(student=student, evaluated_class=evaluated_class,
                                            trimester=current_trimester.name,
                                            hebrew_year=current_trimester.hebrew_school_year)
                    evaluation.clean()
                    evaluation.save()

        # TODO: Figure this part out. Is the filter correct?
        for evaluation in Evaluation.objects.filter(hebrew_year=current_trimester.hebrew_school_year,
                                                    trimester=current_trimester.name):
            try:
                evaluation.clean()
            except StudentNotInClassError:
                evaluation.delete()


@login_required
def write_class_evaluations(request, class_id):
    current_trimester = get_current_trimester()

    teacher = request.user
    try:
        class_to_evaluate = Class.objects.get(id=class_id, teacher=teacher,
                                              hebrew_year=current_trimester.hebrew_school_year)
    except Class.DoesNotExist:
        return redirect(reverse('mismatched_professional_teacher_error'))

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
                                    queryset=Evaluation.objects.filter(hebrew_year=current_trimester.hebrew_school_year,
                                                                       trimester=current_trimester.name))
        formset.save()

    else:
        formset = EvaluationFormSet(instance=class_to_evaluate,
                                    queryset=Evaluation.objects.filter(hebrew_year=current_trimester.hebrew_school_year,
                                                                       trimester=current_trimester.name))

    context = {'formset': formset, 'teacher': teacher, 'class': class_to_evaluate}
    return render(request, 'evaluations/write_evaluations.html', context)


@login_required
def write_evaluations_main_page(request):
    current_trimester = get_current_trimester()
    teacher = request.user

    populate_evaluations_in_teachers_classes(teacher)

    if teacher:
        classes = teacher.class_set.filter(hebrew_year=current_trimester.hebrew_school_year)
    else:
        classes = []

    classes = sorted(classes.all(), key=lambda klass: klass.name)

    context = {'classes': classes, 'teacher': teacher}
    return render(request, 'evaluations/write_evaluations_index.html', context)


@login_required
def view_student_evaluations(request, student_id):
    teacher = request.user

    if not teacher.is_homeroom_teacher:
        return redirect(reverse('not_homeroom_teacher_error'))

    student = Student.objects.get(id=student_id)

    if student.homeroom_teacher != teacher:
        return redirect(reverse('mismatched_homeroom_teacher_error'))

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

    students = sorted(students, key=lambda student: (student.first_name, student.last_name))
    context = {'students': students, 'teacher': teacher}
    return render(request, 'evaluations/view_evaluations_index.html', context)


@login_required
def evaluations_details(request, student_id):
    teacher = request.user
    current_trimester = get_current_trimester()

    if not teacher.is_homeroom_teacher:
        return redirect(reverse('not_homeroom_teacher_error'))

    student = Student.objects.get(id=student_id)

    missing_classes = []
    evaluated_classes = []

    for evaluation in student.evaluations.filter(trimester=current_trimester.name,
                                                 hebrew_year=current_trimester.hebrew_school_year):
        if evaluation.evaluation_text:
            evaluated_classes.append(evaluation.evaluated_class)
        else:
            missing_classes.append(evaluation.evaluated_class)

    context = {
        'student': student, 'missing_classes': missing_classes, 'evaluated_classes': evaluated_classes,
        'teacher': teacher
    }
    return render(request, 'evaluations/evaluation_details.html', context)


def failed_login(request):
    return render(request, 'evaluations/failed_login.html')
