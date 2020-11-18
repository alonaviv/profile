from django.forms import ModelForm, HiddenInput, Form, ModelMultipleChoiceField, CheckboxSelectMultiple
from evaluations.models import Class


class ClassForm(ModelForm):
  class Meta:
      model = Class
      exclude = ['students']
      widgets = {'teacher': HiddenInput()}
      labels = {'name': 'שם השיעור', 'subject': "מקצוע", 'house': "שכבה"}

class AddStudentsForm(Form):
    def __init__(self, *args, **kwargs):  
        """
        Pass the field 'all_students', with all the students to select from.
        Pass the field 'current_students', with the students that are already selected.
        """
        all_students = kwargs.pop('all_students')
        current_students = kwargs.pop('current_students')
        super().__init__(*args, **kwargs)

        self.fields['students'] = ModelMultipleChoiceField(all_students, widget=CheckboxSelectMultiple, label="", initial=current_students)

