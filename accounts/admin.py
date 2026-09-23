from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import TeacherUser


class CustomUserAdmin(UserAdmin):
    def teacher_external_id(self, user: TeacherUser):
        teacher = user.teacher_object
        return teacher.external_id[:8] if teacher and teacher.external_id else None

    teacher_external_id.short_description = "ת.ז. hash"

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'fields': ('is_homeroom_teacher', 'house', 'teacher_object', 'reminders_subscription'),
        }),
    )

    fieldsets = UserAdmin.fieldsets + (
        (None, {
            'fields': ('is_homeroom_teacher', 'house', 'teacher_object', 'reminders_subscription'),
        }),
    )
    list_display = (
        'username',
        'first_name',
        'last_name',
        'is_homeroom_teacher',
        'house',
        'teacher_object',
        'teacher_external_id',
        'email',
        'last_login',
        'date_joined',
    )

    list_filter = ('teacher_object__is_deleted',)


admin.site.register(TeacherUser, CustomUserAdmin)
