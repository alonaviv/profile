from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, reverse


@login_required
def cancel_subscription(request):
    teacher = request.user
    teacher.reminders_subscription = False
    teacher.full_clean()
    teacher.save()

    return redirect(reverse('index'))


@login_required
def restore_subscription(request):
    teacher = request.user
    teacher.reminders_subscription = True
    teacher.full_clean()
    teacher.save()

    return redirect(reverse('index'))
