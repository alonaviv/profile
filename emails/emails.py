from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from profile_server.pronouns import PronounWordDictionary
from profile_server.settings import EMAIL_HOST_USER, DOMAIN

FROM_EMAIL = "מערכת הדיווחים - דמוקרטי כפר סבא" + f" <{EMAIL_HOST_USER}>"


def send_forgot_password_email(teacher):
    context = {
        "email": teacher.email,
        "uid": urlsafe_base64_encode(force_bytes(teacher.pk)),
        "teacher": teacher,
        'token': default_token_generator.make_token(teacher),
        'pronoun_dict': PronounWordDictionary(teacher.pronoun_as_enum),
        'domain': DOMAIN
    }

    subject = "מערכת הדיווחים של הדמוקרטי - בקשה לאיפוס סיסמא"
    raw_template_name = "password_reset_email.txt"
    html_template_name = "password_reset_html_email.txt"
    send_email(html_template_name, raw_template_name, subject, [teacher.email], context)


def send_evaluations_status_update(trimester, teacher, classes, homeroom_students, homeroom_students_without_classes,
                                   teachers_missing_evaluations):
    context = {
        "trimester": trimester,
        "teacher": teacher,
        "classes": classes,
        "homeroom_students": homeroom_students,
        "homeroom_students_without_classes": homeroom_students_without_classes,
        "teachers_missing_evaluations": teachers_missing_evaluations,
        "pronoun_dict": PronounWordDictionary(teacher.pronoun_as_enum),
        "domain": DOMAIN
    }
    subject = f"מערכת הדיווחים של הדמוקרטי - תזכורת: יש לך עוד {trimester.days_left_for_writing} ימים להגשת הדיווחים "
    html_template_name = "evaluations_status_update.txt"
    raw_template_name = html_template_name

    send_email(html_template_name, raw_template_name, subject, [teacher.email], context)


def send_email(html_template_name, raw_template_name, subject, recipient_list, context):
    html_email = render_to_string(f"common/emails/{html_template_name}", context)
    raw_email = render_to_string(f"common/emails/{raw_template_name}", context)
    send_mail(subject, raw_email, FROM_EMAIL, recipient_list,
              fail_silently=False, html_message=html_email)
