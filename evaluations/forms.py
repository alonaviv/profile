from django.forms import ModelForm, HiddenInput, modelformset_factory

from .models import Evaluation


class EvaluationForm(ModelForm):
    class Meta:
        model = Evaluation
        fields = ['student', 'evaluated_class', 'trimester', 'evaluation_text']
        widgets = {'student': HiddenInput(), 'evaluated_class': HiddenInput(), 'trimester': HiddenInput()}

EvaluationFormSet = modelformset_factory(Evaluation, fields=['student', 'evaluated_class', 'trimester',
                                         'evaluation_text'], extra=0)
