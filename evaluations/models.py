from django.db.models import (
    CharField, ForeignKey, ManyToManyField, Model, DO_NOTHING, SmallIntegerField, TextField,
    BooleanField, EmailField, OneToOneField, CASCADE
)
from django.contrib.auth.models import User


class House(Model):
    house_name = CharField(max_length=20, unique=True)

    def __str__(self):
        return self.house_name


class Teacher(Model):
    first_name = CharField(max_length=20)
    last_name = CharField(max_length=30)
    email = EmailField()
    is_homeroom_teacher = BooleanField()
    house = ForeignKey(House, on_delete=DO_NOTHING)
    # TODO: Take off the null
    user = OneToOneField(User, on_delete=CASCADE, null=True)

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
    house = ForeignKey(House, on_delete=DO_NOTHING)
    # To be later added when the homeroom teachers add their kids
    # TODO: Important!! Have a running task that makes sure all kids have a homeroom teacher.
    homeroom_teacher = ForeignKey(Teacher, on_delete=DO_NOTHING, blank=True, null=True)

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
    subject = ForeignKey(Subject, on_delete=DO_NOTHING)
    house = ForeignKey(House, on_delete=DO_NOTHING)
    teacher = ForeignKey(Teacher, on_delete=DO_NOTHING, default=1)
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


class Evaluation(Model):
    student = ForeignKey(Student, on_delete=DO_NOTHING)
    evaluated_class = ForeignKey(Class, on_delete=DO_NOTHING)
    trimester = SmallIntegerField(choices=((1, 'First meeting'), (2, 'Second meeting'), (3, 'Third meeting')))
    evaluation_text = TextField(default='', blank=True)

    class Meta:
        unique_together = ['student', 'evaluated_class', 'trimester']
