from django.core.exceptions import ValidationError
from django.db.models import (
    CharField, ForeignKey, ManyToManyField, Model, TextField, PROTECT,
    IntegerField, BooleanField, Manager
)

from accounts.models import TeacherUser
from profile_server.pronouns import PronounOptions
from utils.date_helpers import TrimesterType
from utils.school_dates import get_current_trimester


class StudentNotInClassError(ValidationError):
    pass


class SoftDeleteManager(Manager):
    def __init__(self, *args, **kwargs):
        self.with_deleted = kwargs.pop('with_deleted', False)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        all_objects = super().get_queryset().all()

        if self.with_deleted:
            return all_objects

        return all_objects.filter(is_deleted=False)


class SoftDeleteModel(Model):
    class Meta:
        abstract = True

    objects = SoftDeleteManager()
    objects_with_deleted = SoftDeleteManager(with_deleted=True)

    is_deleted = BooleanField(null=False, default=False)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.full_clean()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.full_clean()
        self.save()

    def hard_delete(self):
        super(SoftDeleteModel, self).delete()


class House(SoftDeleteModel):
    house_name = CharField(max_length=20, unique=True)

    def __str__(self):
        return self.house_name


class Teacher(SoftDeleteModel):
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


class Student(SoftDeleteModel):
    first_name = CharField(max_length=30)
    last_name = CharField(max_length=30)
    house = ForeignKey(House, on_delete=PROTECT)
    pronoun_choice = CharField(max_length=30, choices=[(pronoun_option.name, pronoun_option.value)
                                                       for pronoun_option in PronounOptions], null=True)
    # To be later added when the homeroom teachers add their kids
    homeroom_teacher = ForeignKey(TeacherUser, on_delete=PROTECT, blank=True, null=True)

    @property
    def completed_evals(self):
        completed_evals = 0
        for evaluation in self.evaluations.filter(is_submitted=True):
            if evaluation.evaluation_text:
                completed_evals += 1

        return completed_evals

    class Meta:
        unique_together = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def completed_evals_in_current_trimester(self):
        current_trimester = get_current_trimester()

        completed_evals = []
        for evaluation in self.evaluations.filter(trimester=current_trimester.name,
                                                  hebrew_year=current_trimester.hebrew_school_year,
                                                  is_submitted=True):
            if evaluation.evaluation_text:
                completed_evals.append(evaluation)

        return completed_evals

    @property
    def all_evals_in_current_trimester(self):
        current_trimester = get_current_trimester()
        return list(self.evaluations.filter(trimester=current_trimester.name,
                                            hebrew_year=current_trimester.hebrew_school_year))

    @property
    def classes_current_year(self):
        current_year = get_current_trimester().hebrew_school_year
        return list(self.classes.filter(hebrew_year=current_year))

    @property
    def num_classes(self):
        return self.classes.count()


class Class(SoftDeleteModel):
    name = CharField(max_length=100)
    subject = ForeignKey(Subject, on_delete=PROTECT)
    house = ForeignKey(House, on_delete=PROTECT)
    teacher = ForeignKey(TeacherUser, on_delete=PROTECT)
    students = ManyToManyField(Student, blank=True, related_name='classes')
    hebrew_year = IntegerField()

    class Meta:
        verbose_name_plural = "Classes"
        unique_together = ('name', 'hebrew_year', 'teacher')

    def __str__(self):
        return self.name

    @property
    def completed_evals_in_current_trimester(self):
        current_trimester = get_current_trimester()

        completed_evals = []
        for evaluation in self.evaluation_set.filter(trimester=current_trimester.name,
                                                     hebrew_year=current_trimester.hebrew_school_year,
                                                     is_submitted=True):
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
    is_submitted = BooleanField(default=False)  # An evaluation that isn't submitted is considered a draft

    class Meta:
        unique_together = ['student', 'evaluated_class', 'trimester']

    def clean(self):
        if self.is_submitted and self.is_empty:
            raise ValidationError("Empty evaluation can not be submitted")

    @property
    def is_student_in_class(self):
        return self.student in self.evaluated_class.students.all()

    @property
    def is_empty(self):
        return not self.evaluation_text or self.evaluation_text.isspace()
