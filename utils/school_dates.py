from datetime import datetime

from profile_config import STUDENT_MEETING_DATES, GRACE_PERIOD, EVALUATION_DEADLINE_DAYS
from utils.date_helpers import TrimesterType, Trimester


def get_current_trimester():
    current_date = datetime.now()

    first_trimester = Trimester(TrimesterType.FIRST_TRIMESTER, STUDENT_MEETING_DATES['first_meeting'].as_datetime(),
                                GRACE_PERIOD, EVALUATION_DEADLINE_DAYS)
    second_trimester = Trimester(TrimesterType.SECOND_TRIMESTER, STUDENT_MEETING_DATES['second_meeting'].as_datetime(),
                                 GRACE_PERIOD, EVALUATION_DEADLINE_DAYS)
    third_trimester = Trimester(TrimesterType.THIRD_TRIMESTER, STUDENT_MEETING_DATES['third_meeting'].as_datetime(),
                                GRACE_PERIOD, EVALUATION_DEADLINE_DAYS)
    null_trimester = Trimester(TrimesterType.NULL_TRIMESTER)

    if current_date >= third_trimester.actual_end_of_trimester:
        return null_trimester
    elif current_date >= second_trimester.actual_end_of_trimester:
        return third_trimester
    elif current_date >= first_trimester.actual_end_of_trimester:
        return second_trimester
    else:
        return first_trimester
