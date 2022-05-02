from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, reverse, redirect
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from unidecode import unidecode

from profile_server.pronouns import PronounWordDictionary
from utils.date_helpers import get_printable_date
from utils.school_dates import get_current_trimester
from .models import Evaluation, Class, Student

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
    If there isn't, create an entry with empty text.
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
                    evaluation.full_clean()
                    evaluation.save()


@login_required
def write_class_evaluations(request, class_id, anchor=None):
    current_trimester = get_current_trimester()

    teacher = request.user
    try:
        class_to_evaluate = Class.objects.get(id=class_id, hebrew_year=current_trimester.hebrew_school_year)
    except Class.DoesNotExist:
        return render(request, 'common/general_error_page.html',
                      {'error_message': 'השיעור המבוקש אינו קיים במערכת'})

    if class_to_evaluate.teacher != teacher:
        return render(request, 'common/general_error_page.html',
                      {'error_message': 'רק המורה של השיעור רשאי/ת לכתוב דיווחים'})

    if request.method == 'POST':
        evaluation = Evaluation.objects.get(id=request.POST['evaluation_id'])
        if 'evaluation_text' in request.POST:
            evaluation.evaluation_text = request.POST['evaluation_text']
        error_encountered = False

        if 'save_draft' in request.POST:  # Saves new text, while remaining unsubmitted
            if evaluation.is_submitted:
                return render(request, 'common/general_error_page.html',
                              {'error_message': 'לא ניתן לשמור טיוטא של דיווח שכבר נשלח'})

        elif 'submit' in request.POST:
            evaluation.is_submitted = True

            if evaluation.is_empty:
                messages.error(request, "לא ניתן להגיש דיווח ריק.", extra_tags=str(evaluation.id))
                error_encountered = True

        elif 'withdraw' in request.POST:
            evaluation.is_submitted = False

        else:
            return render(request, 'common/general_error_page.html',
                          {'error_message': 'תקלה בשליחת הדיווח'})

        if not error_encountered:
            evaluation.full_clean()
            evaluation.save()

    evaluations = Evaluation.objects.filter(evaluated_class=class_to_evaluate,
                                            trimester=current_trimester.name).order_by('student')

    if not anchor:
        anchor = f"anchor_{request.POST['evaluation_id']}" if 'evaluation_id' in request.POST else 'top'

    context = {
        'teacher': teacher, 'class': class_to_evaluate, 'evaluations': evaluations,
        'anchor': anchor
    }
    return render(request, 'evaluations/write_evaluations.html', context)


@login_required
def remove_evaluation(request, evaluation_id):
    teacher = request.user
    evaluation = Evaluation.objects.get(id=evaluation_id)

    if evaluation.is_submitted:
        messages.error(request, "לא ניתן לבטל דיווח שכבר נשלח לחונכ/ת", extra_tags=str(evaluation.id))

        return redirect(
            reverse('write_class_evaluations_with_anchor',
                    args=(evaluation.evaluated_class.id, f"anchor_{evaluation_id}")))

    if not evaluation.is_empty:
        messages.error(request,
                       "לא ניתן לבטל דיווח כאשר קיימת טיוטא. אם ברצונך לבטל את הדיווח בכל זאת, יש לשמור טיוטא ריקה.",
                       extra_tags=str(evaluation.id))

        return redirect(
            reverse('write_class_evaluations_with_anchor',
                    args=(evaluation.evaluated_class.id, f"anchor_{evaluation_id}")))

    if teacher != evaluation.evaluated_class.teacher:
        return render(request, 'common/general_error_page.html',
                      {'error_message': 'רק המורה של השיעור רשאי/ת להסיר דיווחים של השיעור'})
    if evaluation.is_student_in_class:
        return render(request, 'common/general_error_page.html',
                      {'error_message': 'לא ניתן להסיר דיווח של תלמיד/ה שעדיין נמצא/ת בשיעור'})

    evaluation.delete()

    return redirect(
        reverse('write_class_evaluations_with_anchor', args=(evaluation.evaluated_class.id, f"anchor_{evaluation_id}")))


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


def _get_student_evaluation_context(request, student_id):
    teacher = request.user

    if not teacher.is_homeroom_teacher:
        return redirect(reverse('not_homeroom_teacher_error'))

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return render(request, 'common/general_error_page.html',
                      {'error_message': 'תלמיד/ה זה/זו לא נמצא/ת בבית הספר'})

    if student.homeroom_teacher != teacher:
        return redirect(reverse('mismatched_homeroom_teacher_error'))

    pronoun_dict = PronounWordDictionary(teacher.pronoun_as_enum)

    return {'student': student, 'teacher': teacher, 'pronoun_dict': pronoun_dict,
            'trimester': get_current_trimester(), 'printable_date': get_printable_date()}


@login_required
def view_student_evaluations(request, student_id):
    context = _get_student_evaluation_context(request, student_id)

    if isinstance(context, HttpResponse):
        return context

    return render(request, 'evaluations/view_evaluations.html', context)


@login_required
def view_single_eval(request, evaluation_id):
    context = {'evaluation': Evaluation.objects.get(id=evaluation_id)}

    return render(request, 'evaluations/display_single_eval.html', context)


@login_required
def download_student_evaluations(request, student_id):
    context = _get_student_evaluation_context(request, student_id)

    if isinstance(context, HttpResponse):
        return context

    response = HttpResponse(content_type="application/pdf")

    trimester_name = context['trimester'].name.lower().replace("_"," ")
    trimester_year = context['trimester'].meeting_end_of_trimester.year
    filename = f"School reports for {unidecode(str(context['student']))} - {trimester_name} {trimester_year}"
    response['Content-Disposition'] = f"attachment; filename={filename}.pdf"
    html_string = render_to_string("evaluations/evaluations_as_pdf.html", context)
    with open('profile_server/static/css/style_for_pdf.css') as f:
        css_string = f.read()

    HTML(string=html_string).write_pdf(response, stylesheets=[CSS(string=css_string)])
    return response


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

    evaluations = student.evaluations.filter(trimester=current_trimester.name,
                                             hebrew_year=current_trimester.hebrew_school_year).order_by(
        'evaluation_text')
    context = {
        'student': student, 'evaluations': evaluations, 'teacher': teacher
    }
    return render(request, 'evaluations/evaluation_details.html', context)


def failed_login(request):
    return render(request, 'evaluations/failed_login.html')
