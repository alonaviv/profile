from django.db.models import BooleanField, EmailField, ForeignKey, OneToOneField, CharField, PROTECT 
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import AbstractBaseUser
from .managers import TeacherUserManager

class TeacherUser(AbstractUser):
    is_homeroom_teacher = BooleanField()

    # Allowing NULL in order to make superuser creation easier. Will make sure that when regular user is created, we pass these fields.
    house = ForeignKey('evaluations.House', on_delete=PROTECT, null=True)
    teacher_object = OneToOneField('evaluations.Teacher', on_delete=PROTECT, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
      
    
    
    
    objects = TeacherUserManager()
