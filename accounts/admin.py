from django.contrib import admin
from .models import TeacherUser
from django.contrib.auth.admin import UserAdmin


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
    list_display = ('username', 'first_name', 'last_name', 'is_homeroom_teacher', 'house', 'teacher_object', 'email')


admin.site.register(TeacherUser, CustomUserAdmin)
