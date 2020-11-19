from django.db.models import (
    CharField, ForeignKey, ManyToManyField, Model, DO_NOTHING, SmallIntegerField, TextField, PROTECT,
    BooleanField, EmailField, OneToOneField, CASCADE, SET_NULL, CheckConstraint
)
from django.core.exceptions import ValidationError
from accounts.models import TeacherUser


class StudentNotInClassError(ValidationError):
    pass


class House(Model):
    house_name = CharField(max_length=20, unique=True)

    def __str__(self):
        return self.house_name


class Teacher(Model):
    """
    This model is only used to verify that the TeacherUser is created based on an existing teacher in school.
    We'll populate all the school teachers with this model before allowing them to create users.
    """
    first_name = CharField(max_length=20)
    last_name = CharField(max_length=30)

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
    homeroom_teacher = ForeignKey(TeacherUser, on_delete=SET_NULL, blank=True, null=True)

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
    teacher = ForeignKey(TeacherUser, on_delete=PROTECT)
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
