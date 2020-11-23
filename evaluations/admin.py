from django.contrib import admin

from .models import Class, Teacher, Subject, House, Student, Evaluation


class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'evaluated_class', 'trimester', 'hebrew_year')
    list_display_links = ('id', 'student', 'evaluated_class')

    list_filter = ('student', 'evaluated_class', 'trimester')


class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'subject', 'house', 'teacher', 'hebrew_year')
    list_display_links = ('id', 'name')

    list_filter = ('house', 'subject')


class TeacherAdmin(admin.ModelAdmin):
    def _get_string(self, model):
        return str(model)

    list_display = ('id', 'first_name', 'last_name')
    list_display_links = ('id', 'first_name', 'last_name')


class StudentAdmin(admin.ModelAdmin):
    def _get_string(self, model):
        return str(model)

    def _get_classes(self, model):
        return ', '.join(str(student_class) for student_class in model.class_set.all())

    _get_classes.short_description = 'Classes'
    _get_string.short_description = 'Student Name'

    list_display = ('id', '_get_string', 'homeroom_teacher', 'house', '_get_classes')
    list_display_links = ('id', '_get_string')
    list_filter = ('homeroom_teacher', 'house')


admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Subject)
admin.site.register(House)
admin.site.register(Student, StudentAdmin)
