from django.forms import modelformset_factory

from .models import Evaluation

EvaluationFormSet = modelformset_factory(Evaluation, fields=['student', 'evaluated_class', 'trimester',
                                                             'evaluation_text'], extra=0)
