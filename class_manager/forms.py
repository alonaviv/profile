from django.forms import (
    ModelForm, Form, CheckboxSelectMultiple, MultipleChoiceField
)

from evaluations.models import Class


class ClassForm(ModelForm):
    class Meta:
        model = Class
        exclude = ['students', 'teacher', 'hebrew_year', 'is_deleted']
        labels = {'name': 'שם השיעור', 'subject': "מקצוע", 'house': "שכבה"}


class AddStudentsForm(Form):
    def __init__(self, *args, **kwargs):
        # Django isn't able to sort hebrew correxctly - so we have to use raw python instead.
        students = kwargs.pop('students')
        students_sorted = sorted(students.all(), key=lambda student: (student.first_name, student.last_name))
        student_choices = [(student.id, str(student)) for student in students_sorted]

        super().__init__(*args, **kwargs)

        # self.fields['students'] = ModelMultipleChoiceField(all_students_sorted, widget=CheckboxSelectMultiple, label="",
        #                                                    initial=current_students)
        self.fields['students'] = MultipleChoiceField(choices=student_choices, widget=CheckboxSelectMultiple)
        self.fields['students'].label = ""
