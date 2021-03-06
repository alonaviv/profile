from django.contrib import admin

from .models import Class, Teacher, Subject, House, Student, Evaluation


class SoftDeletionAdmin(admin.ModelAdmin):
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
    list_display = ('id', 'student', 'evaluated_class', 'evaluation_text', 'trimester', 'hebrew_year')
    list_display_links = ('id', 'student', 'evaluated_class')

    list_filter = ('student', 'evaluated_class', 'trimester')


class ClassAdmin(SoftDeletionAdmin):
    list_display = ('id', 'name', 'subject', 'house', 'teacher', 'hebrew_year')
    list_display_links = ('id', 'name')

    list_filter = ('house', 'subject')


class TeacherAdmin(SoftDeletionAdmin):
    def _get_string(self, model):
        return str(model)

    list_display = ('id', 'first_name', 'last_name')
    list_display_links = ('id', 'first_name', 'last_name')


class StudentAdmin(SoftDeletionAdmin):
    def _get_string(self, model):
        return str(model)

    def _get_classes(self, model):
        return ', '.join(str(student_class) for student_class in model.classes.all())

    _get_classes.short_description = 'Classes'
    _get_string.short_description = 'Student Name'

    list_display = ('id', '_get_string', 'homeroom_teacher', 'house', 'pronoun_choice', '_get_classes')
    list_display_links = ('id', '_get_string')
    list_filter = ('homeroom_teacher', 'house')


admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Subject)
admin.site.register(House)
admin.site.register(Student, StudentAdmin)
