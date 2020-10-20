from django.forms import ModelForm, HiddenInput, modelformset_factory

from .models import Evaluation


class EvaluationForm(ModelForm):
    class Meta:
        model = Evaluation
        fields = ['student', 'evaluated_class', 'trimester', 'evaluation_text']
        widgets = {'student': HiddenInput(), 'evaluated_class': HiddenInput(), 'trimester': HiddenInput()}

# TODO Need to use formset, because we really need one form per evaluation.
# TODO: A single evaluation is defined by a combination of the class, student and trimester. All thses
# TODO: We get from the form. If it's all one big form it doesn't work - you don't know what belongs to what.
# TODO: Seems like there's no way around it - need to use javascript to create a new copy of the form and add it
# TODO: to the form set


EvaluationFormSet = modelformset_factory(Evaluation, fields=['student', 'evaluated_class', 'trimester',
                                         'evaluation_text'], extra=0)

