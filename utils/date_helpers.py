from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum, auto

from hebrew_numbers import int_to_gematria
from pyluach import dates


# Note: All this would have been a lot easier by using hebrew years for the school year natively, and only converting to
# Gregorian when needed, but it's no fun testing it with hebrew years - so I decided to do it in a way I can easily
# convert myself.

class TrimesterType(Enum):
    FIRST_TRIMESTER = 1
    SECOND_TRIMESTER = 2
    THIRD_TRIMESTER = 3
    NULL_TRIMESTER = 0  # After third meeting and in summer vacation

    @classmethod
    def get_choices(cls):
        """
        Generate the format required for choices field in django models.
        The value name of the enum is actually what we want to pass as the value.
        """
        return [(field.name, field.name) for field in cls]


@dataclass
class SchoolDay:
    day: int
    month: int

    def as_datetime(self, year=None):
        """
        If year isn't passed, gets the correct year for this date based on the current school year.
        """
        if not year:
            year = get_year_of_trimester(self)
        return datetime(year, self.month, self.day)

    # All comparisons use a mock year - it doesn't matter what year it is, as long as they are the same
    def __eq__(self, other):
        return self.as_datetime(1492) == other.as_datetime(1492)

    def __lt__(self, other):
        return self.as_datetime(1492) < other.as_datetime(1492)

    def __gt__(self, other):
        return self.as_datetime(1492) > other.as_datetime(1492)

    def __ge__(self, other):
        return self.as_datetime(1492) >= other.as_datetime(1492)

    def __le__(self, other):
        return self.as_datetime(1492) <= other.as_datetime(1492)


class Trimester:
    def __init__(self, trimester_name: TrimesterType, meeting_end_of_trimester: datetime = None,
                 grace_period: int = None):
        self.number = trimester_name.value
        self.name = trimester_name.name
        self.meeting_end_of_trimester = meeting_end_of_trimester
        self.grace_period = grace_period

    @property
    def meeting_end_of_trimester_printable(self):
        return self.meeting_end_of_trimester.strftime("%d/%m/%y")

    @property
    def hebrew_school_year_printable(self):
        """Returns the text of the year as usually written, without the ה at the start"""
        return int_to_gematria(self.hebrew_school_year - 5000)

    @property
    def gregorian_school_year(self):
        """
        In a school year of 2020-2021, this should be 2020.
        If there is no meeting at the end of the trimester (probably since it's summer vacation), returns according
        to the current date)
        """
        return get_gregorian_school_year(self.meeting_end_of_trimester)

    @property
    def actual_end_of_trimester(self):
        if self.meeting_end_of_trimester and self.grace_period:
            return self.meeting_end_of_trimester + timedelta(days=self.grace_period)
        else:
            return None

    @property
    def hebrew_school_year(self):
        # Choosing a date that is for sure after Rosh Hashana
        gregorian_start_of_year_date = dates.GregorianDate(self.gregorian_school_year, 11, 16)
        return gregorian_start_of_year_date.to_heb().year


def get_gregorian_school_year(current_date=None):
    """If the school year is 2020-2021, this gives 2020"""
    if not current_date:
        current_date = datetime.now()

    if current_date >= START_OF_YEAR.as_datetime(current_date.year):
        return current_date.year
    else:
        return current_date.year - 1


def get_year_of_trimester(meeting_date, current_date=None, year_start_of_school=None):
    """
    Return the gregorian year of the given meeting that kicks off the trimester.
    Should not be called for the first trimester, as it doesn't have a meeting at the start.

    If the trimester starts on 03/11, we need to know what year that date is. This can only be determined by knowing
    what school year we're in (2020-2021, or 2021-2022).
    So we first calculate what school year we're in (represented by the first of the two gregorian years).
    Then, we look at the date of the given meeting date in order to determine in which of the two years it's in.
    """

    if not year_start_of_school:
        if not current_date:
            current_date = datetime.now()

        year_start_of_school = get_gregorian_school_year(current_date)

    if meeting_date >= START_OF_YEAR:
        return year_start_of_school
    else:
        return year_start_of_school + 1


START_OF_YEAR = SchoolDay(1, 9)
