from django.core.management.base import BaseCommand
from emails.send_emails import send_evaluations_status_update
from accounts.models import TeacherUser
from utils.school_dates import get_current_trimester
from dashboard.views import get_dashboard_context


class Command(BaseCommand):
    help = "Send email to all teachers, updating them about the status of their evaluations"

    def add_arguments(self, parser):
        parser.add_argument('--emails', nargs='+', type=str, required=False)

    def handle(self, *args, **options):
        if options['emails']:
            teachers = TeacherUser.objects.filter(email__in=options['emails'], teacher_object__is_deleted=False)
        else:
            teachers = TeacherUser.objects.filter(reminders_subscription=True, teacher_object__is_deleted=False)

        for teacher in teachers:
            # Don't send emails to teacher who are only professional teachers, and already completed everything
            if not (not teacher.is_homeroom_teacher and teacher.all_evals_in_current_trimester == teacher.completed_evals_in_current_trimester):
                dashboard_context = get_dashboard_context(teacher)
                send_evaluations_status_update(
                    teacher=teacher,
                    trimester=get_current_trimester(),
                    classes=dashboard_context['classes'],
                    homeroom_students=dashboard_context['homeroom_students'],
                    homeroom_students_without_classes=dashboard_context['homeroom_students_without_classes'],
                    teachers_missing_evaluations=dashboard_context['teachers_missing_evaluations'],
                )
