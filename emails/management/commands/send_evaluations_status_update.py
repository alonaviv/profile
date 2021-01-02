from django.core.management.base import BaseCommand
from emails.emails import send_evaluations_status_update
from accounts.models import TeacherUser
from utils.school_dates import get_current_trimester
from dashboard.views import get_dashboard_context


class Command(BaseCommand):
    help = "Send and email to all teachers, updating them about the status of their evaluations"

    def handle(self, *args, **options):
        # for teacher in TeacherUser.objects.all():
        for teacher in TeacherUser.objects.filter(email='alona@infinidat.com'):
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
