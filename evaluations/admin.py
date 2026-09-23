from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import CharField, ModelForm
from import_export.admin import ExportActionModelAdmin

from .models import Class, Teacher, Subject, House, Student, Evaluation
from .roster_import import hash_ministry_id, is_valid_israeli_id, normalize_ministry_id
from accounts.models import TeacherUser


class SoftDeletionAdmin(ExportActionModelAdmin, admin.ModelAdmin):
    def get_queryset(self, request):
        query_set = self.model.objects_with_deleted

        # The below is copied from the base implementation in BaseModelAdmin to prevent other changes in behavior
        ordering = self.get_ordering(request)
        if ordering:
            query_set = query_set.order_by(*ordering)

        return query_set

    def delete_model(self, request, obj):
        obj.hard_delete()


class EvaluationAdmin(admin.ModelAdmin):
    def get_homeroom_teacher(self, evaluation):
        return evaluation.student.homeroom_teacher
    get_homeroom_teacher.admin_order_field = 'homeroom_teacher'  #Allows column order sorting
    get_homeroom_teacher.short_description = 'Homeroom Teacher'  #Renames column head

    list_display = ('id', 'student', 'evaluated_class', 'evaluation_text', 'trimester', 'hebrew_year',
                    'get_homeroom_teacher')
    list_display_links = ('id', 'student', 'evaluated_class')

    list_filter = ('student', 'evaluated_class', 'trimester', 'student__homeroom_teacher')


class ClassAdmin(SoftDeletionAdmin):
    list_display = ('id', 'name', 'subject', 'house', 'teacher', 'hebrew_year')
    list_display_links = ('id', 'name')

    list_filter = ('house', 'subject')


class TeacherAdmin(SoftDeletionAdmin):
    def _get_string(self, model):
        return str(model)

    def has_user(self, teacher: Teacher):
        return TeacherUser.objects.filter(teacher_object=teacher).exists()

    has_user.boolean = True
    has_user.short_description = "Has User"

    list_display = ('id', 'first_name', 'last_name', 'has_user')
    list_display_links = ('id', 'first_name', 'last_name')
    list_filter = ('is_deleted',)


class StudentAddForm(ModelForm):
    """Adding a student requires the ministry id, so next year's ministry file matches them. Only its hash is kept."""
    ministry_id = CharField(label='ת.ז. תלמיד', max_length=12, help_text="Stored only as a salted hash")

    class Meta:
        model = Student
        fields = ('first_name', 'last_name', 'house', 'pronoun_choice', 'homeroom_teacher')

    def clean_ministry_id(self):
        try:
            ministry_id = normalize_ministry_id(self.cleaned_data['ministry_id'])
        except ValueError as e:
            raise ValidationError(str(e))
        if not is_valid_israeli_id(ministry_id):
            raise ValidationError("Invalid ת.ז. (check digit doesn't match)")

        external_id = hash_ministry_id(ministry_id, settings.STUDENT_ID_SALT)
        existing = Student.objects_with_deleted.filter(external_id=external_id).first()
        if existing:
            deleted = ", soft-deleted - restore it instead" if existing.is_deleted else ""
            raise ValidationError(f"This ת.ז. belongs to student {existing.id} ({existing}{deleted})")
        return external_id

    def save(self, commit=True):
        self.instance.external_id = self.cleaned_data['ministry_id']
        return super().save(commit)


class StudentAdmin(SoftDeletionAdmin):
    def _get_classes(self, model):
        return ', '.join(str(student_class) for student_class in model.classes.all())

    _get_classes.short_description = 'Classes'

    list_display = ('id', 'first_name', 'last_name', 'homeroom_teacher', 'house', 'pronoun_choice', '_get_classes')
    list_display_links = ('id',)
    list_filter = ('homeroom_teacher', 'house', 'is_deleted')
    ordering = ('first_name', 'house')

    list_per_page = 500

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs['form'] = StudentAddForm
        return super().get_form(request, obj, **kwargs)


admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Subject)
admin.site.register(House)
admin.site.register(Student, StudentAdmin)
