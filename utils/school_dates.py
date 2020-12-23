from datetime import datetime, timedelta

from hebrew_numbers import int_to_gematria
from pyluach import dates

from trimesters_config import STUDENT_MEETING_DATES, GRACE_PERIOD
from utils.date_helpers import Trimester, get_year_start_of_school


def get_hebrew_year_as_int(current_date=None):
    """
    Returns the hebrew date of the current school year, using the mark for the end of the year
    """
    if not current_date:
        current_date = datetime.now()

    year_start_of_school = get_year_start_of_school(current_date)
    gregorian_start_of_year_date = dates.GregorianDate(year_start_of_school, 11, 1)  # Day/Month is irrelevant here
    return gregorian_start_of_year_date.to_heb().year


def get_hebrew_year_as_hebrew_letters(hebrew_year_in_int):
    """Returns the text of the year as usually written, without the ה at the start"""
    return int_to_gematria(hebrew_year_in_int - 5000)


def get_current_trimester_and_hebrew_year():
    current_date = datetime.now()

    second_trimester_start_date = STUDENT_MEETING_DATES['first_meeting'].as_datetime() + timedelta(days=GRACE_PERIOD)
    third_trimester_start_date = STUDENT_MEETING_DATES['second_meeting'].as_datetime() + timedelta(days=GRACE_PERIOD)
    null_trimester_start_date = STUDENT_MEETING_DATES['third_meeting'].as_datetime() + timedelta(days=GRACE_PERIOD)

    if current_date >= null_trimester_start_date:
        trimester = Trimester.NULL_TRIMESTER
    elif current_date >= third_trimester_start_date:
        trimester = Trimester.THIRD_TRIMESTER
    elif current_date >= second_trimester_start_date:
        trimester = Trimester.SECOND_TRIMESTER
    else:
        trimester = Trimester.FIRST_TRIMESTER

    return trimester, get_hebrew_year_as_int(current_date)
