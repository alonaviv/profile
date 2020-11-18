from django.db.models import (
    CharField, ForeignKey, ManyToManyField, Model, DO_NOTHING, SmallIntegerField, TextField, PROTECT,
    BooleanField, EmailField, OneToOneField, CASCADE, SET_NULL, CheckConstraint
)
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class StudentNotInClassError(ValidationError):
    pass


class House(Model):
    house_name = CharField(max_length=20, unique=True)

    def __str__(self):
        return self.house_name


class Teacher(Model):
    first_name = CharField(max_length=20)
    last_name = CharField(max_length=30)
    email = EmailField()
    is_homeroom_teacher = BooleanField()
    house = ForeignKey(House, on_delete=PROTECT)
    user = OneToOneField(User, on_delete=SET_NULL, null=True)

    class Meta:
        unique_together = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Subject(Model):
    subject_name = CharField(max_length=100, unique=True)

    def __str__(self):
        return self.subject_name


class Student(Model):
    first_name = CharField(max_length=20)
    last_name = CharField(max_length=30)
    house = ForeignKey(House, on_delete=PROTECT)
    # To be later added when the homeroom teachers add their kids
    homeroom_teacher = ForeignKey(Teacher, on_delete=SET_NULL, blank=True, null=True)

    @property
    def completed_evals(self):
        completed_evals = 0
        for evaluation in self.evaluation_set.all():
            if evaluation.evaluation_text:
                completed_evals += 1
        
        return completed_evals

    class Meta:
        unique_together = ['first_name', 'last_name', 'house']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Class(Model):
    name = CharField(max_length=100, unique=True)
    subject = ForeignKey(Subject, on_delete=PROTECT)
    house = ForeignKey(House, on_delete=PROTECT)
    teacher = ForeignKey(Teacher, on_delete=PROTECT, default=1)
    students = ManyToManyField(Student, blank=True)

    @property
    def completed_evals(self):
        completed_evals = 0
        for evaluation in self.evaluation_set.all():
            if evaluation.evaluation_text:
                completed_evals += 1
        
        return completed_evals

    class Meta:
        verbose_name_plural = "Classes"

    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        if self.students.count() >  0:
            raise ValueError("Cannot delete class that has students")
        else:
            super().delete(*args, **kwargs)



class Evaluation(Model):
    student = ForeignKey(Student, on_delete=CASCADE)
    evaluated_class = ForeignKey(Class, on_delete=CASCADE)
    trimester = SmallIntegerField(choices=((1, 'First meeting'), (2, 'Second meeting'), (3, 'Third meeting')))
    evaluation_text = TextField(default='', blank=True)

    class Meta:
        unique_together = ['student', 'evaluated_class', 'trimester']
    
    def clean(self):
        if self.student not in self.evaluated_class.students.all():
            raise StudentNotInClassError("The student of this evaluation doesn't match the class")
