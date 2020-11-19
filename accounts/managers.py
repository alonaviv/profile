from django.contrib.auth.models import BaseUserManager, UserManager


class TeacherUserManager(BaseUserManager):
    def create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')

        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_homeroom_teacher', True)
        extra_fields.setdefault('house', None)
        extra_fields.setdefault('teacher_object', None)

        return self.create_user(username, email, password, **extra_fields)