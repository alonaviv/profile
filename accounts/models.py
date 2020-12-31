from django.contrib.auth.models import AbstractUser
from django.db.models import BooleanField, ForeignKey, OneToOneField, PROTECT, EmailField, CharField

from profile_server.pronouns import PronounOptions, PronounWordDictionary
from .managers import TeacherUserManager


class TeacherUser(AbstractUser):
    is_homeroom_teacher = BooleanField()
    email = EmailField(unique=True)

    # Allowing NULL in order to make superuser creation easier. Will make sure that when regular user is created,
    # we pass these fields.
    house = ForeignKey('evaluations.House', on_delete=PROTECT, null=True)
    teacher_object = OneToOneField('evaluations.Teacher', on_delete=PROTECT, null=True)
    pronoun_choice = CharField(max_length=30, choices=[(pronoun_option.name, pronoun_option.value)
                                                       for pronoun_option in PronounOptions], null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    objects = TeacherUserManager()

    @property
    def pronoun_as_enum(self):
        if not self.pronoun_choice:
            return PronounOptions.FEMALE

        return PronounOptions[self.pronoun_choice]

    @property
    def completed_evals_in_current_trimester(self):
        completed_evals = []
        for klass in self.class_set.all():
            completed_evals.extend(klass.completed_evals_in_current_trimester)

        return completed_evals

    @property
    def all_evals_in_current_trimester(self):
        all_evals = []
        for klass in self.class_set.all():
            all_evals.extend(klass.all_evals_in_current_trimester)

        return all_evals

    @property
    def evals_percentage_completed(self):
        return 100 * (len(self.completed_evals_in_current_trimester) / len(self.all_evals_in_current_trimester))

    @property
    def completed_evals_of_homeroom_students_in_current_trimester(self):
        completed_evals = []
        for student in self.student_set.all():
            completed_evals.extend(student.completed_evals_in_current_trimester)

        return completed_evals

    @property
    def all_evals_of_homeroom_students_in_current_trimester(self):
        all_evals = []
        for student in self.student_set.all():
            all_evals.extend(student.all_evals_in_current_trimester)

        return all_evals

    @property
    def missing_evals_of_homeroom_students_in_current_trimester(self):
        return [evaluation for evaluation in self.all_evals_of_homeroom_students_in_current_trimester if
                evaluation not in self.completed_evals_of_homeroom_students_in_current_trimester]

    @property
    def printable_description(self):
        return PronounWordDictionary(self.pronoun_as_enum)['mentor'] + " - " + str(self)
