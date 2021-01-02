from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from validations.run_validations import all_validations


@login_required
def validations_summary(request):
    teacher = request.user
    validation_results = [validation() for validation in all_validations]
    context = {'teacher': teacher, 'validation_results': validation_results}

    return render(request, 'validations/validations_summary.html', context)
