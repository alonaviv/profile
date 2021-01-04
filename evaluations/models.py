from django.core.exceptions import ValidationError
from django.db.models import (
    CharField, ForeignKey, ManyToManyField, Model, TextField, PROTECT,
    SET_NULL, IntegerField, BooleanField
)

from accounts.models import TeacherUser
from utils.school_dates import get_current_trimester
from utils.date_helpers import TrimesterType


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
    first_name = CharField(max_length=30)
    last_name = CharField(max_length=30)
    house = ForeignKey(House, on_delete=PROTECT)
    # To be later added when the homeroom teachers add their kids
    homeroom_teacher = ForeignKey(TeacherUser, on_delete=SET_NULL, blank=True, null=True)
    is_deleted = BooleanField(default=False)

    @property
    def completed_evals(self):
        completed_evals = 0
        for evaluation in self.evaluations.all():
            if evaluation.evaluation_text:
                completed_evals += 1

        return completed_evals

    class Meta:
        unique_together = ['first_name', 'last_name', 'house']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def completed_evals_in_current_trimester(self):
        current_trimester = get_current_trimester()

        completed_evals = []
        for evaluation in self.evaluations.filter(trimester=current_trimester.name,
                                                     hebrew_year=current_trimester.hebrew_school_year):
            if evaluation.evaluation_text:
                completed_evals.append(evaluation)

        return completed_evals

    @property
    def all_evals_in_current_trimester(self):
        current_trimester = get_current_trimester()
        return list(self.evaluations.filter(trimester=current_trimester.name,
                                            hebrew_year=current_trimester.hebrew_school_year))

    @property
    def num_classes(self):
        return self.classes.count()


class Class(Model):
    name = CharField(max_length=100)
    subject = ForeignKey(Subject, on_delete=PROTECT)
    house = ForeignKey(House, on_delete=PROTECT)
    teacher = ForeignKey(TeacherUser, on_delete=PROTECT)
    students = ManyToManyField(Student, blank=True, related_name='classes')
    hebrew_year = IntegerField()
    is_deleted = BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Classes"
        unique_together = ('name', 'hebrew_year')

    def __str__(self):
        return self.name

    @property
    def completed_evals_in_current_trimester(self):
        current_trimester = get_current_trimester()

        completed_evals = []
        for evaluation in self.evaluation_set.filter(trimester=current_trimester.name,
                                                     hebrew_year=current_trimester.hebrew_school_year):
            if evaluation.evaluation_text:
                completed_evals.append(evaluation)

        return completed_evals

    @property
    def all_evals_in_current_trimester(self):
        current_trimester = get_current_trimester()
        return list(self.evaluation_set.filter(trimester=current_trimester.name,
                                               hebrew_year=current_trimester.hebrew_school_year))


class Evaluation(Model):
    # Students, Classes, Teachers and Evaluations should never be deleted. Only marked as is_deleted.
    # We don't ever want to lose information about an evaluation, and what student/class/teacher it was related to.
    student = ForeignKey(Student, on_delete=PROTECT, related_name='evaluations')
    evaluated_class = ForeignKey(Class, on_delete=PROTECT)
    evaluation_text = TextField(default='', blank=True)
    hebrew_year = IntegerField()
    trimester = CharField(choices=TrimesterType.get_choices(), max_length=20)

    class Meta:
        unique_together = ['student', 'evaluated_class', 'trimester']

    @property
    def is_student_in_class(self):
        return self.student in self.evaluated_class.students.filter(is_deleted=False)

    @property
    def is_submitted(self):
        return self.evaluation_text and not self.evaluation_text.isspace()
