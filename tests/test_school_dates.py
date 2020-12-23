from datetime import datetime

import pytest
from freezegun import freeze_time
from mock import patch

from utils.date_helpers import Trimester, SchoolDay, get_year_start_of_school, get_year_of_trimester_start
from utils.school_dates import (
    get_current_trimester_and_hebrew_year
)

trimester_config1 = {
    "first_meeting": SchoolDay(15, 10),
    "second_meeting": SchoolDay(10, 12),
    "third_meeting": SchoolDay(20, 4),
}

trimester_config2 = {
    "first_meeting": SchoolDay(14, 11),
    "second_meeting": SchoolDay(2, 1),
    "third_meeting": SchoolDay(1, 5),
}


@patch('utils.school_dates.STUDENT_MEETING_DATES', trimester_config1)
@patch('utils.school_dates.GRACE_PERIOD', 2)
@pytest.mark.parametrize("current_date, expected_trimester, expected_year",
                         [
                             ("2020-06-30", Trimester.NULL_TRIMESTER, 5780),
                             ("2020-07-30", Trimester.NULL_TRIMESTER, 5780),
                             ("2020-08-01", Trimester.NULL_TRIMESTER, 5780),
                             ("2020-08-31", Trimester.NULL_TRIMESTER, 5780),
                             ("2020-09-01", Trimester.FIRST_TRIMESTER, 5781),
                             ("2020-10-01", Trimester.FIRST_TRIMESTER, 5781),
                             ("2020-10-15", Trimester.FIRST_TRIMESTER, 5781),
                             ("2020-10-16", Trimester.FIRST_TRIMESTER, 5781),
                             ("2020-10-17", Trimester.SECOND_TRIMESTER, 5781),
                             ("2020-11-30", Trimester.SECOND_TRIMESTER, 5781),
                             ("2020-12-01", Trimester.SECOND_TRIMESTER, 5781),
                             ("2020-12-10", Trimester.SECOND_TRIMESTER, 5781),
                             ("2020-12-11", Trimester.SECOND_TRIMESTER, 5781),
                             ("2020-12-12", Trimester.THIRD_TRIMESTER, 5781),
                             ("2021-01-01", Trimester.THIRD_TRIMESTER, 5781),
                             ("2021-03-01", Trimester.THIRD_TRIMESTER, 5781),
                             ("2021-03-31", Trimester.THIRD_TRIMESTER, 5781),
                             ("2021-04-01", Trimester.THIRD_TRIMESTER, 5781),
                             ("2021-04-20", Trimester.THIRD_TRIMESTER, 5781),
                             ("2021-04-21", Trimester.THIRD_TRIMESTER, 5781),
                             ("2021-04-22", Trimester.NULL_TRIMESTER, 5781),
                             ("2021-07-01", Trimester.NULL_TRIMESTER, 5781),
                             ("2021-07-20", Trimester.NULL_TRIMESTER, 5781),
                             ("2021-08-20", Trimester.NULL_TRIMESTER, 5781),
                             ("2021-09-01", Trimester.FIRST_TRIMESTER, 5782)
                         ])
def test_get_current_year_and_trimester_config1(current_date, expected_trimester, expected_year):
    with freeze_time(current_date):
        assert get_current_trimester_and_hebrew_year() == (expected_trimester, expected_year)


@patch('utils.school_dates.STUDENT_MEETING_DATES', trimester_config2)
@patch('utils.school_dates.GRACE_PERIOD', 2)
@pytest.mark.parametrize("current_date, expected_trimester, expected_year",
                         [
                             ("2021-04-30", Trimester.THIRD_TRIMESTER, 5781),
                             ("2021-05-01", Trimester.THIRD_TRIMESTER, 5781),
                             ("2021-05-03", Trimester.NULL_TRIMESTER, 5781),
                             ("2021-05-30", Trimester.NULL_TRIMESTER, 5781),
                             ("2021-06-30", Trimester.NULL_TRIMESTER, 5781),
                             ("2021-07-01", Trimester.NULL_TRIMESTER, 5781),
                             ("2021-07-31", Trimester.NULL_TRIMESTER, 5781),
                             ("2021-08-01", Trimester.NULL_TRIMESTER, 5781),
                             ("2021-08-31", Trimester.NULL_TRIMESTER, 5781),
                             ("2021-09-01", Trimester.FIRST_TRIMESTER, 5782),
                             ("2021-10-15", Trimester.FIRST_TRIMESTER, 5782),
                             ("2021-11-14", Trimester.FIRST_TRIMESTER, 5782),
                             ("2021-11-16", Trimester.SECOND_TRIMESTER, 5782),
                             ("2021-11-30", Trimester.SECOND_TRIMESTER, 5782),
                             ("2021-12-01", Trimester.SECOND_TRIMESTER, 5782),
                             ("2022-01-01", Trimester.SECOND_TRIMESTER, 5782),
                             ("2022-03-01", Trimester.THIRD_TRIMESTER, 5782),
                             ("2022-03-31", Trimester.THIRD_TRIMESTER, 5782),
                             ("2022-04-01", Trimester.THIRD_TRIMESTER, 5782),
                             ("2022-04-30", Trimester.THIRD_TRIMESTER, 5782),
                             ("2022-05-01", Trimester.THIRD_TRIMESTER, 5782),
                             ("2022-05-03", Trimester.NULL_TRIMESTER, 5782),
                             ("2022-07-01", Trimester.NULL_TRIMESTER, 5782),
                             ("2022-07-20", Trimester.NULL_TRIMESTER, 5782),
                             ("2022-08-20", Trimester.NULL_TRIMESTER, 5782),
                             ("2022-09-01", Trimester.FIRST_TRIMESTER, 5783),
                             ("2022-09-20", Trimester.FIRST_TRIMESTER, 5783)
                         ])
def test_get_current_year_and_trimester_config2(current_date, expected_trimester, expected_year):
    with freeze_time(current_date):
        assert get_current_trimester_and_hebrew_year() == (expected_trimester, expected_year)


def test_get_current_year_and_trimester_no_mock():
    trimester, year = get_current_trimester_and_hebrew_year()
    assert isinstance(trimester, Trimester)
    assert isinstance(year, int)


@pytest.mark.parametrize("current_date, expected_start_of_school",
                         [
                             ("2020-11-30", 2020),
                             ("2021-06-30", 2020),
                             ("2021-05-30", 2020),
                             ("2021-07-31", 2020),
                             ("2021-08-01", 2020),
                             ("2021-08-31", 2020),
                             ("2021-09-01", 2021),
                             ("2021-11-30", 2021),
                             ("2021-12-01", 2021),
                             ("2022-01-01", 2021),
                             ("2022-03-01", 2021),
                             ("2022-03-31", 2021),
                             ("2022-04-01", 2021),
                             ("2022-04-30", 2021),
                             ("2022-05-01", 2021),
                             ("2022-07-01", 2021),
                             ("2022-07-20", 2021),
                             ("2022-08-20", 2021),
                             ("2022-09-01", 2022),
                         ])
def test_get_year_start_of_school(current_date, expected_start_of_school):
    with freeze_time(current_date):
        assert get_year_start_of_school(datetime.now()) == expected_start_of_school


@pytest.mark.parametrize("current_date, trimester_start, expected_start_of_school",
                         [
                             ("2021-05-30", SchoolDay(5, 10), 2020),
                             ("2021-06-30", SchoolDay(5, 10), 2020),
                             ("2021-07-30", SchoolDay(5, 10), 2020),
                             ("2021-08-01", SchoolDay(5, 10), 2020),
                             ("2021-08-31", SchoolDay(5, 10), 2020),
                             ("2021-09-01", SchoolDay(5, 10), 2021),
                             ("2021-11-30", SchoolDay(5, 10), 2021),
                             ("2021-12-01", SchoolDay(5, 10), 2021),
                             ("2022-01-01", SchoolDay(5, 10), 2021),
                             ("2022-03-01", SchoolDay(5, 10), 2021),
                             ("2022-03-31", SchoolDay(5, 10), 2021),
                             ("2022-04-01", SchoolDay(5, 10), 2021),
                             ("2022-04-30", SchoolDay(5, 10), 2021),
                             ("2022-05-01", SchoolDay(5, 10), 2021),
                             ("2022-07-01", SchoolDay(5, 10), 2021),
                             ("2022-07-20", SchoolDay(5, 10), 2021),
                             ("2022-08-20", SchoolDay(5, 10), 2021),
                             ("2022-09-20", SchoolDay(5, 10), 2022)
                         ])
def test_get_year_of_trimester_start_using_start_of_year(current_date, trimester_start, expected_start_of_school):
    with freeze_time(current_date):
        assert get_year_of_trimester_start(trimester_start) == expected_start_of_school


@pytest.mark.parametrize("current_date, trimester_start, expected_start_of_school",
                         [
                             ("2021-05-30", SchoolDay(9, 1), 2021),
                             ("2021-06-30", SchoolDay(9, 1), 2021),
                             ("2021-07-30", SchoolDay(9, 1), 2021),
                             ("2021-08-01", SchoolDay(9, 1), 2021),
                             ("2021-08-31", SchoolDay(9, 1), 2021),
                             ("2021-09-01", SchoolDay(9, 1), 2022),
                             ("2021-11-30", SchoolDay(9, 1), 2022),
                             ("2021-12-01", SchoolDay(9, 1), 2022),
                             ("2022-01-01", SchoolDay(9, 1), 2022),
                             ("2022-03-01", SchoolDay(9, 1), 2022),
                             ("2022-03-31", SchoolDay(9, 1), 2022),
                             ("2022-04-01", SchoolDay(9, 1), 2022),
                             ("2022-04-30", SchoolDay(9, 1), 2022),
                             ("2022-05-01", SchoolDay(9, 1), 2022),
                             ("2022-07-01", SchoolDay(9, 1), 2022),
                             ("2022-07-20", SchoolDay(9, 1), 2022),
                             ("2022-08-20", SchoolDay(9, 1), 2022),
                             ("2022-09-20", SchoolDay(9, 1), 2023)
                         ])
def test_get_year_of_trimester_start_using_middle_of_year(current_date, trimester_start, expected_start_of_school):
    with freeze_time(current_date):
        assert get_year_of_trimester_start(trimester_start) == expected_start_of_school


@pytest.mark.parametrize("current_date, trimester_start, expected_start_of_school",
                         [
                             ("2021-05-30", SchoolDay(5, 8), 2021),
                             ("2021-06-30", SchoolDay(5, 8), 2021),
                             ("2021-07-30", SchoolDay(5, 8), 2021),
                             ("2021-08-01", SchoolDay(5, 8), 2021),
                             ("2021-08-31", SchoolDay(5, 8), 2021),
                             ("2021-09-01", SchoolDay(5, 8), 2022),
                             ("2021-11-30", SchoolDay(5, 8), 2022),
                             ("2021-12-01", SchoolDay(5, 8), 2022),
                             ("2022-01-01", SchoolDay(5, 8), 2022),
                             ("2022-03-01", SchoolDay(5, 8), 2022),
                             ("2022-03-31", SchoolDay(5, 8), 2022),
                             ("2022-04-01", SchoolDay(5, 8), 2022),
                             ("2022-04-30", SchoolDay(5, 8), 2022),
                             ("2022-05-01", SchoolDay(5, 8), 2022),
                             ("2022-07-01", SchoolDay(5, 8), 2022),
                             ("2022-07-20", SchoolDay(5, 8), 2022),
                             ("2022-08-20", SchoolDay(5, 8), 2022),
                             ("2022-09-20", SchoolDay(5, 8), 2023)
                         ])
def test_get_year_of_trimester_start_using_end_of_year(current_date, trimester_start, expected_start_of_school):
    with freeze_time(current_date):
        assert get_year_of_trimester_start(trimester_start) == expected_start_of_school
