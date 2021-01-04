from utils.school_dates import get_current_trimester
from .pronouns import PronounWordDictionary


def pronoun_dict_context_processor(request):
    teacher = request.user

    if not teacher.is_anonymous:
        pronoun_dict = PronounWordDictionary(teacher.pronoun_as_enum)
    else:
        pronoun_dict = {}

    return {'pronoun_dict': pronoun_dict}


def trimester_context_processor(request):
    return {'trimester': get_current_trimester()}


def teacher_context_processor(request):
    teacher = request.user
    return {'teacher': teacher}
