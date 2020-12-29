from utils.school_dates import get_current_trimester
from .pronouns import PronounWordDictionary, PronounOptions


def trimester_context_processor(request):
    teacher = request.user

    if not teacher.is_anonymous and not teacher.is_superuser:
        pronoun_dict = PronounWordDictionary(teacher.pronoun_as_enum)
    else:
        pronoun_dict = {}

    return {'trimester': get_current_trimester(), 'pronoun_dict': pronoun_dict}

