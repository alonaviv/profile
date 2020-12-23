from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum


class Trimester(IntEnum):
    FIRST_TRIMESTER = 1
    SECOND_TRIMESTER = 2
    THIRD_TRIMESTER = 3
    NULL_TRIMESTER = 4  # After third meeting and in summer vacation

    @classmethod
    def get_choices(cls):
        """
        Generate the format required for choices field in django models
        """
        return [(field.value, field.name) for field in cls]


@dataclass
class SchoolDay:
    day: int
    month: int

    def as_datetime(self, year=None):
        """
        If year isn't passed, gets the correct year for this date based on the current school year.
        """
        if not year:
            year = get_year_of_trimester_start(self)
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


START_OF_YEAR = SchoolDay(1, 9)


def get_year_start_of_school(current_date=None):
    """If the school year is 2020-2021, this gives 2020"""
    if not current_date:
        current_date = datetime.now()

    if current_date >= START_OF_YEAR.as_datetime(current_date.year):
        return current_date.year
    else:
        return current_date.year - 1


def get_year_of_trimester_start(meeting_date, current_date=None):
    """
    Return the gregorian year of the given meeting that kicks off the trimester.
    Should not be called for the first trimester, as it doesn't have a meeting at the start.

    If the trimester starts on 03/11, we need to know what year that date is. This can only be determined by knowing
    what school year we're in (2020-2021, or 2021-2022).
    So we first calculate what school year we're in (represented by the first of the two gregorian years).
    Then, we look at the date of the given meeting date in order to determine in which of the two years it's in.
    """
    if not current_date:
        current_date = datetime.now()

    year_start_of_school = get_year_start_of_school(current_date)

    if meeting_date >= START_OF_YEAR:
        return year_start_of_school
    else:
        return year_start_of_school + 1
