from django.core.management.base import BaseCommand
from accounts.models import TeacherUser
from emails.send_emails import send_urgent_validations_email
from validations.run_validations import urgent_validations


class Command(BaseCommand):
    help = "Run all validation tests, and send results to all staff"

    def add_arguments(self, parser):
        parser.add_argument('--staff_emails', nargs='+', type=str)

    def handle(self, *args, **options):
        if options['staff_emails']:
            teachers = TeacherUser.objects.filter(email__in=options['emails'], is_staff=True)
        else:
            teachers = TeacherUser.objects.filter(is_staff=True)

        validation_results = [validation() for validation in urgent_validations]
        failed_validation_results = [validation_result for validation_result in validation_results if
                                     not validation_result.bool_result]
        for teacher in teachers:
            send_urgent_validations_email(teacher, failed_validation_results)
