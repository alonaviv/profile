from utils.school_dates import get_current_trimester


def trimester_context_processor(request):
    return {'trimester': get_current_trimester()}

