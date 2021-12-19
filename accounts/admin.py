from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import TeacherUser


class CustomUserAdmin(UserAdmin):
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
    'username', 'first_name', 'last_name', 'is_homeroom_teacher', 'house', 'teacher_object', 'email', 'last_login')

    list_filter = ('teacher_object__is_deleted',)


admin.site.register(TeacherUser, CustomUserAdmin)
