from functools import wraps
from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, reverse, redirect
from django.template.loader import render_to_string
from hebrew_numbers import int_to_gematria
from weasyprint import HTML, CSS
from unidecode import unidecode

from profile_server.pronouns import PronounWordDictionary, PronounOptions
from utils.date_helpers import get_printable_date, TrimesterType
from utils.school_dates import get_current_trimester
from .models import Evaluation, Class, Student, House

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


# ==== Historic evaluations download (admin-only) - any year/semester ===

# Only the three real trimesters are exposed - the null
# trimester is intentionally absent.
_HISTORIC_TRIMESTER_HEBREW_LABELS = {
    1: 'פגישה מספר 1 (ראשונה, מעט דיווחים)',
    2: 'פגישה מספר 2',
    3: 'פגישה מספר 3',
}


def _historic_staff_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            return render(request, 'common/general_error_page.html',
                          {'error_message': 'רק משתמשים בעלי הרשאת ניהול רשאים לצפות בעמוד זה'})
        return view_func(request, *args, **kwargs)

    return wrapped


def _historic_hebrew_year_label(hebrew_year):
    """Same convention as Trimester.hebrew_school_year_printable (e.g. 'תשפ״ה')."""
    return int_to_gematria(hebrew_year - 5000)


class _HistoricTrimester:
    """
    Minimal stand-in for `utils.date_helpers.Trimester` that exposes only the
    attributes the PDF template reads. A real Trimester is built from school
    config (meeting dates / grace period) and can't represent arbitrary
    historical year+trimester pairs without that config, so we use this shim.
    """

    def __init__(self, trimester_number, hebrew_year):
        self.number = trimester_number
        self._hebrew_year = hebrew_year

    @property
    def hebrew_school_year_printable(self):
        return _historic_hebrew_year_label(self._hebrew_year)


class _HistoricStudent:
    """
    Read-only proxy around a real `Student` used only when rendering an historic
    PDF. The shared template `evaluations/evaluations_as_pdf.html` pulls its
    evaluations via:

        {% with all_student_evals=student.all_evals_in_current_trimester
                completed_student_evals=student.completed_evals_in_current_trimester %}

    so to render an arbitrary historical year/semester without modifying the
    template, we hand it a student-like object whose
    `*_evals_in_current_trimester` properties return the data for the requested
    historic year+trimester instead of the actual current trimester. Every other
    attribute (first_name, last_name, house, homeroom_teacher, ...) is delegated
    to the wrapped Student via `__getattr__`, so the rest of the template
    renders identically.
    """

    def __init__(self, student, hebrew_year, trimester_name):
        self._student = student
        self._hebrew_year = hebrew_year
        self._trimester_name = trimester_name

    def __getattr__(self, name):
        return getattr(self._student, name)

    def __str__(self):
        return str(self._student)

    @property
    def completed_evals_in_current_trimester(self):
        # Mirrors Student.completed_evals_in_current_trimester verbatim, but
        # for the requested historic year+trimester.
        completed_evals = []
        for evaluation in self._student.evaluations.filter(
                trimester=self._trimester_name,
                hebrew_year=self._hebrew_year,
                is_submitted=True):
            if evaluation.evaluation_text:
                completed_evals.append(evaluation)
        return completed_evals

    @property
    def all_evals_in_current_trimester(self):
        # Mirrors Student.all_evals_in_current_trimester verbatim, but for
        # the requested historic year+trimester.
        return list(self._student.evaluations.filter(
            trimester=self._trimester_name,
            hebrew_year=self._hebrew_year))


def _historic_submitted_evals_for_student(student):
    return student.evaluations.filter(is_submitted=True).exclude(evaluation_text='')


@_historic_staff_required
def historic_index(request):
    houses = House.objects.order_by('house_name')
    return render(request, 'evaluations/historic_index.html', {'houses': houses})


@_historic_staff_required
def historic_house(request, house_id):
    try:
        house = House.objects.get(id=house_id)
    except House.DoesNotExist:
        return render(request, 'common/general_error_page.html',
                      {'error_message': 'הבית המבוקש אינו קיים במערכת'})
    students = Student.objects.filter(house=house).order_by('first_name', 'last_name')
    return render(request, 'evaluations/historic_students.html',
                  {'house': house, 'students': students})


@_historic_staff_required
def historic_student(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return render(request, 'common/general_error_page.html',
                      {'error_message': 'תלמיד/ה זה/זו לא נמצא/ת בבית הספר'})

    years = sorted(
        set(_historic_submitted_evals_for_student(student).values_list('hebrew_year', flat=True)),
        reverse=True,
    )
    year_entries = [{'hebrew_year': y, 'label': _historic_hebrew_year_label(y)} for y in years]
    return render(request, 'evaluations/historic_years.html',
                  {'student': student, 'year_entries': year_entries})


@_historic_staff_required
def historic_student_year(request, student_id, hebrew_year):
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return render(request, 'common/general_error_page.html',
                      {'error_message': 'תלמיד/ה זה/זו לא נמצא/ת בבית הספר'})

    trimester_names = set(
        _historic_submitted_evals_for_student(student)
        .filter(hebrew_year=hebrew_year)
        .values_list('trimester', flat=True)
    )

    semester_entries = []
    for trimester_name in trimester_names:
        try:
            number = TrimesterType[trimester_name].value
        except KeyError:
            continue
        if number in _HISTORIC_TRIMESTER_HEBREW_LABELS:
            semester_entries.append(
                {'number': number, 'label': _HISTORIC_TRIMESTER_HEBREW_LABELS[number]}
            )
    semester_entries.sort(key=lambda entry: entry['number'])

    context = {
        'student': student,
        'hebrew_year': hebrew_year,
        'hebrew_year_label': _historic_hebrew_year_label(hebrew_year),
        'semester_entries': semester_entries,
    }
    return render(request, 'evaluations/historic_semesters.html', context)


@_historic_staff_required
def historic_download(request, student_id, hebrew_year, trimester_num):
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return render(request, 'common/general_error_page.html',
                      {'error_message': 'תלמיד/ה זה/זו לא נמצא/ת בבית הספר'})

    if trimester_num not in _HISTORIC_TRIMESTER_HEBREW_LABELS:
        return render(request, 'common/general_error_page.html',
                      {'error_message': 'סמסטר לא תקין'})
                 
    trimester_name = TrimesterType(trimester_num).name

    homeroom_teacher = student.homeroom_teacher
    if homeroom_teacher is not None:
        pronoun_dict = PronounWordDictionary(homeroom_teacher.pronoun_as_enum)
        teacher_for_template = homeroom_teacher
    else:
        # Fallback used only when no homeroom teacher is currently assigned to
        # the student (e.g. graduated). Keeps the PDF rendering safe; the rest
        # of the document - the evaluations themselves - is unchanged.
        pronoun_dict = PronounWordDictionary(PronounOptions.FEMALE)
        teacher_for_template = '— אין מחנך/ת נוכחי/ת —'
   

    context = {
        # Wrap the student so the shared PDF template's
        # `{% with ... =student.completed_evals_in_current_trimester %}` block
        # surfaces the historical evals for the requested year+semester instead
        # of the current trimester's. Every other attribute is delegated to the
        # real Student via the proxy.
        'student': _HistoricStudent(student, hebrew_year, trimester_name),
        'teacher': teacher_for_template,
        'pronoun_dict': pronoun_dict,
        'trimester': _HistoricTrimester(trimester_num, hebrew_year),
        # The PDF template renders this string in its top-corner banner.
        # For the live teacher download it's just today's date - a "printed on"
        # stamp. For a historic download we additionally flag the document as
        # historical so a parent reading the PDF doesn't mistake it for a
        # fresh report.
        'printable_date': f'דיווח היסטורי - הופק {get_printable_date()}',
    }

    html_string = render_to_string('evaluations/evaluations_as_pdf.html', context)
    with open('profile_server/static/css/style_for_pdf.css') as f:
        css_string = f.read()

    response = HttpResponse(content_type='application/pdf')
    # Filename format requested by the user (note the double space after the dash):
    # "<Hebrew student name> -  Year <hebrew year>, semester <n>"
    filename = (
        f"{student} -  "
        f"Year {_historic_hebrew_year_label(hebrew_year)}, semester {trimester_num}.pdf"
    )
    response['Content-Disposition'] = f"attachment; filename*=UTF-8''{quote(filename)}"

    HTML(string=html_string).write_pdf(response, stylesheets=[CSS(string=css_string)])
    return response
