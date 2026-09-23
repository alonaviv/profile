"""Page /evaluations/import_roster, once a year: upload the ministry file, preview the plan, apply it."""
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect
from django.shortcuts import render

from evaluations.models import House, Student
from evaluations.roster_import import DbStudent, MinistryFileError, plan_import, read_ministry_file


class RosterImportForm(forms.Form):
    ministry_file = forms.FileField(label="Ministry file (אלפון מלא)")
    password = forms.CharField(required=False, widget=forms.PasswordInput,
                               help_text="If the file is password-protected")
    new_school_year = forms.BooleanField(required=False, label="New school year",
                                         help_text="Also clear every homeroom teacher")
    apply = forms.BooleanField(required=False, help_text="Leave unticked to preview. Ticked, writes the plan "
                                                         "unless it has errors")


@login_required
def import_roster_view(request):
    if not request.user.is_superuser:
        return render(request, 'common/general_error_page.html',
                      {'error_message': 'רק משתמשים בעלי הרשאת ניהול רשאים לצפות בעמוד זה'})

    form = RosterImportForm(request.POST or None, request.FILES or None)
    context = {'form': form}
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        try:
            ministry_rows = read_ministry_file(data['ministry_file'].file, data['password'], settings.STUDENT_ID_SALT)
        except MinistryFileError as e:
            form.add_error(None, str(e))
        else:
            with transaction.atomic():
                plan = plan_import(ministry_rows, _db_students())
                if data['apply'] and not plan.errors:
                    _apply(plan, data['new_school_year'], request)
                    return redirect('import_roster')
            context['plan'] = plan
    return render(request, 'evaluations/import_roster.html', context)


def _db_students():
    return [DbStudent(student.id, student.first_name, student.last_name, student.house.house_name,
                      student.external_id, student.is_deleted)
            for student in Student.objects_with_deleted.select_related('house')]


def _apply(plan, new_school_year, request):
    houses = {house.house_name: house for house in House.objects.all()}
    students = Student.objects_with_deleted.in_bulk([student.db_student.id for student in plan.students_to_update])
    for to_update in plan.students_to_update:
        student = students[to_update.db_student.id]
        student.grade = to_update.ministry_row.grade
        student.house = houses[to_update.new_house]
        student.is_deleted = False
        student.save(update_fields=['grade', 'house', 'is_deleted'])

    for to_create in plan.students_to_create:
        Student.objects.create(first_name=to_create.first_name, last_name=to_create.last_name,
                               house=houses[to_create.house], grade=to_create.grade,
                               external_id=to_create.external_id)

    Student.objects.filter(id__in=[student.id for student in plan.students_to_soft_delete]).update(is_deleted=True)
    if new_school_year:
        Student.objects.update(homeroom_teacher=None)

    messages.success(request, f"Roster imported: {len(plan.students_to_update)} updated, "
                              f"{len(plan.students_to_create)} created, "
                              f"{len(plan.students_to_soft_delete)} soft-deleted"
                              f"{', homeroom teachers cleared' if new_school_year else ''}. "
                              f"Active students: {Student.objects.count()}")
