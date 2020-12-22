from django.core.exceptions import ValidationError
from django.db.models import (
    CharField, ForeignKey, ManyToManyField, Model, TextField, PROTECT,
    CASCADE, SET_NULL, IntegerField, Manager
)

from accounts.models import TeacherUser
from utils.school_dates import Trimester, get_current_trimester_and_hebrew_year


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

    @property
    def completed_evals_in_current_trimester(self):
        current_trimester, current_year = get_current_trimester_and_hebrew_year()

        completed_evals = []
        for evaluation in self.evaluation_set.filter(trimester=current_trimester, hebrew_year=current_year):
            if evaluation.evaluation_text:
                completed_evals.append(evaluation)

        return completed_evals

    @property
    def required_evals_in_current_trimester(self):
        current_trimester, current_year = get_current_trimester_and_hebrew_year()
        return list(self.evaluation_set.get_evaluations_with_active_students().filter(trimester=current_trimester,
                                                                                      hebrew_year=current_year))


class Class(Model):
    name = CharField(max_length=100)
    subject = ForeignKey(Subject, on_delete=PROTECT)
    house = ForeignKey(House, on_delete=PROTECT)
    teacher = ForeignKey(TeacherUser, on_delete=PROTECT)
    students = ManyToManyField(Student, blank=True)
    hebrew_year = IntegerField()

    class Meta:
        verbose_name_plural = "Classes"
        unique_together = ('name', 'hebrew_year')

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        if self.students.count() > 0:
            raise ValueError("Cannot delete class that has students")
        else:
            super().delete(*args, **kwargs)

    # @property
    # def completed_evals_in_current_trimester(self):
    #     current_trimester, current_year = get_current_trimester_and_hebrew_year()
    #
    #     completed_evals = []
    #     for evaluation in self.evaluation_set.filter(trimester=current_trimester, hebrew_year=current_year):
    #         if evaluation.evaluation_text:
    #             completed_evals.append(evaluation)
    #
    #     return completed_evals
    #
    # @property
    # def required_evals_in_current_trimester(self):
    #     current_trimester, current_year = get_current_trimester_and_hebrew_year()
    #     return list(self.evaluation_set.get_evaluations_with_active_students().filter(trimester=current_trimester,
    #                                                                                   hebrew_year=current_year))


class EvaluationManager(Manager):
    def get_evaluations_current_trimester(self):
        evaluations_with_active_students = set()

        for evaluation in self.get_completed_evaluations_including_non_active_students_current_trimester():
            if evaluation.student in evaluation.evaluated_class.students.all():
                evaluations_with_active_students.add(evaluation.pk)

        return self.all().filter(pk__in=evaluations_with_active_students)

    def get_completed_evaluations_current_trimester(self):
        return self.get_evaluations_current_trimester().exclude(evaluation_text='')

    def get_completed_evaluations_including_non_active_students_current_trimester(self):
        current_trimester, current_year = get_current_trimester_and_hebrew_year()
        return self.all().filter(trimester=current_trimester, hebrew_year=current_year)


class Evaluation(Model):
    student = ForeignKey(Student, on_delete=CASCADE)
    evaluated_class = ForeignKey(Class, on_delete=CASCADE)
    evaluation_text = TextField(default='', blank=True)
    hebrew_year = IntegerField()
    trimester = IntegerField(choices=Trimester.get_choices())

    objects = EvaluationManager()

    class Meta:
        unique_together = ['student', 'evaluated_class', 'trimester']

    @property
    def is_student_in_class(self):
        return self.student in self.evaluated_class.students.all()
