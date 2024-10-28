from django.contrib import admin
from import_export.admin import ExportActionModelAdmin

from .models import Class, Teacher, Subject, House, Student, Evaluation


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

    list_display = ('id', 'first_name', 'last_name')
    list_display_links = ('id', 'first_name', 'last_name')
    list_filter = ('is_deleted',)


class StudentAdmin(SoftDeletionAdmin):
    def _get_classes(self, model):
        return ', '.join(str(student_class) for student_class in model.classes.all())

    _get_classes.short_description = 'Classes'

    list_display = ('id', 'first_name', 'last_name', 'homeroom_teacher', 'house', 'pronoun_choice', '_get_classes')
    list_display_links = ('id', '_get_string')
    list_filter = ('homeroom_teacher', 'house', 'is_deleted')
    ordering = ('first_name', 'house')

    list_per_page = 500


admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Subject)
admin.site.register(House)
admin.site.register(Student, StudentAdmin)
