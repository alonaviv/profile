from django.contrib import admin

from .models import Evaluation, Class, Teacher, Subject, House, Student

admin.site.register(Evaluation)
admin.site.register(Class)
admin.site.register(Teacher)
admin.site.register(Subject)
admin.site.register(House)
admin.site.register(Student)
