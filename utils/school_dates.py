from pyluach import dates
from hebrew_numbers import int_to_gematria
from enum import IntEnum
from trimesters_config import TRIMESTERS_CONFIG, END_OF_YEAR_MONTH
from datetime import datetime


class Trimester(IntEnum):
    FIRST_TRIMESTER = 1
    SECOND_TRIMESTER = 2
    THIRD_TRIMESTER = 3

    @classmethod
    def get_choices(cls):
        """
        Generate the format required for choices field in django models
        """
        return [(field.value, field.name) for field in cls]


def get_hebrew_year_as_int(current_date=None):
    """
    Returns the hebrew date of the current school year, using the mark for the end of the year
    """
    if not current_date:
        current_date = datetime.now()
    year_start_of_school = get_year_start_of_school(current_date)
    gregorian_start_of_year_date = dates.GregorianDate(year_start_of_school, 11, 1)
    return gregorian_start_of_year_date.to_heb().year


def get_hebrew_year_as_hebrew_letters(year_in_int):
    """Returns the text of the year as usually written, without the ה at the start"""
    return int_to_gematria(year_in_int - 5000)


def get_year_start_of_school(current_date):
    """If the school year is 2020-2021, this gives 2020"""
    if current_date.month >= END_OF_YEAR_MONTH:
        return current_date.year
    else:
        return current_date.year - 1


def get_year_of_trimester(current_date, trimester_start_month):
    year_start_of_school = get_year_start_of_school(current_date)

    if trimester_start_month >= END_OF_YEAR_MONTH:
        return year_start_of_school
    else:
        return year_start_of_school + 1


def get_current_trimester_and_hebrew_year():
    current_date = datetime.now()

    second_trimester_start_month = TRIMESTERS_CONFIG['second_trimester_start_month']
    second_trimester_start_date = datetime(year=get_year_of_trimester(current_date, second_trimester_start_month),
                                           month=second_trimester_start_month,
                                           day=1)
    third_trimester_start_month = TRIMESTERS_CONFIG['third_trimester_start_month']
    third_trimester_start_date = datetime(year=get_year_of_trimester(current_date, third_trimester_start_month),
                                          month=third_trimester_start_month,
                                          day=1)

    if current_date >= third_trimester_start_date:
        trimester = Trimester.THIRD_TRIMESTER
    elif current_date >= second_trimester_start_date:
        trimester = Trimester.SECOND_TRIMESTER
    else:
        trimester = Trimester.FIRST_TRIMESTER

    return trimester, get_hebrew_year_as_int(current_date)
