from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from validations.run_validations import (
    validate_all_students_have_classes,
    validate_all_students_have_homerooms,
    validate_all_students_have_minimal_amount_of_classes,
    validate_all_students_have_valid_homeroom_teachers,
    validate_all_teachers_have_registered
)


@login_required
def validations_summary(request):
    teacher = request.user

    context = {
        'teacher': teacher, 'students_without_homerooms': validate_all_students_have_homerooms(),
        'students_without_valid_homeroom_teachers': validate_all_students_have_valid_homeroom_teachers(),
        'unregistered_teachers': validate_all_teachers_have_registered(),
        'students_without_classes': validate_all_students_have_classes(),
        'students_with_few_num_of_classes': validate_all_students_have_minimal_amount_of_classes()
    }

    return render(request, 'validations/validations_summary.html', context)
