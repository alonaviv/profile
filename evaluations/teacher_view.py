"""Page /evaluations/import_teachers, once a year: upload the teachers file, preview the plan, apply it."""
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from accounts.models import TeacherUser
from evaluations.models import Teacher
from evaluations.teacher_import import DbTeacher, TeachersFileError, plan_teacher_import, read_teachers_file


class TeacherImportForm(forms.Form):
    teachers_file = forms.FileField(label="Teachers file")
    password = forms.CharField(required=False, widget=forms.PasswordInput,
                               help_text="If the file is password-protected")
    apply = forms.BooleanField(required=False, help_text="Leave unticked to preview. Ticked, writes the plan "
                                                         "unless it has errors")


@login_required
def import_teachers_view(request):
    if not request.user.is_superuser:
        return render(request, 'common/general_error_page.html',
                      {'error_message': 'רק משתמשים בעלי הרשאת ניהול רשאים לצפות בעמוד זה'})

    form = TeacherImportForm(request.POST or None, request.FILES or None)
    context = {'form': form}
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        try:
            file_rows = read_teachers_file(data['teachers_file'].file, data['password'], settings.STUDENT_ID_SALT)
        except TeachersFileError as e:
            form.add_error(None, str(e))
        else:
            with transaction.atomic():
                plan = plan_teacher_import(file_rows, _db_teachers())
                if data['apply'] and not plan.errors:
                    _apply(plan, request)
                    return redirect('import_teachers')
            context['plan'] = plan
    return render(request, 'evaluations/import_teachers.html', context)


def _db_teachers():
    superuser_teacher_ids = set(TeacherUser.objects.filter(is_superuser=True).values_list('teacher_object', flat=True))
    return [DbTeacher(teacher.id, teacher.first_name, teacher.last_name, teacher.external_id, teacher.is_deleted,
                      teacher.id in superuser_teacher_ids)
            for teacher in Teacher.objects_with_deleted.all()]


def _apply(plan, request):
    ids_to_restore = [teacher.id for teacher in plan.teachers_to_restore]
    Teacher.objects_with_deleted.filter(id__in=ids_to_restore).update(is_deleted=False)
    # Only accounts that were in use before: an account that never logged in may still be waiting for email
    # verification, which is also an inactive account
    TeacherUser.objects.filter(teacher_object__in=ids_to_restore, last_login__isnull=False).update(is_active=True)

    for to_create in plan.teachers_to_create:
        Teacher.objects.create(first_name=to_create.first_name, last_name=to_create.last_name,
                               external_id=to_create.external_id)

    ids_to_soft_delete = [teacher.id for teacher in plan.teachers_to_soft_delete]
    Teacher.objects.filter(id__in=ids_to_soft_delete).update(is_deleted=True)
    TeacherUser.objects.filter(teacher_object__in=ids_to_soft_delete, is_superuser=False).update(is_active=False)

    messages.success(request, f"Teachers imported: {len(plan.teachers_to_create)} created, "
                              f"{len(plan.teachers_to_restore)} restored, "
                              f"{len(plan.teachers_to_soft_delete)} soft-deleted and their accounts deactivated. "
                              f"Active teachers: {Teacher.objects.count()}")
