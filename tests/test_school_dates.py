from datetime import datetime

import pytest
from freezegun import freeze_time
from mock import patch

from utils.date_helpers import TrimesterType, SchoolDay, get_gregorian_school_year, get_year_of_trimester
from utils.school_dates import (
    get_current_trimester
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
@pytest.mark.parametrize(
    "current_date, expected_trimester_name, expected_meeting_end_of_trimester, "
    "expected_actual_end_of_trimester, expected_gregorian_school_year, expected_hebrew_school_year",
    [
        ("2020-06-30", TrimesterType.NULL_TRIMESTER, None, None, 2019, 5780),
        ("2020-07-30", TrimesterType.NULL_TRIMESTER, None, None, 2019, 5780),
        ("2020-08-01", TrimesterType.NULL_TRIMESTER, None, None, 2019, 5780),
        ("2020-08-31", TrimesterType.NULL_TRIMESTER, None, None, 2019, 5780),
        ("2020-09-01", TrimesterType.FIRST_TRIMESTER, datetime(2020, 10, 15), datetime(2020, 10, 17), 2020, 5781),
        ("2020-10-01", TrimesterType.FIRST_TRIMESTER, datetime(2020, 10, 15), datetime(2020, 10, 17), 2020, 5781),
        ("2020-10-15", TrimesterType.FIRST_TRIMESTER, datetime(2020, 10, 15), datetime(2020, 10, 17), 2020, 5781),
        ("2020-10-16", TrimesterType.FIRST_TRIMESTER, datetime(2020, 10, 15), datetime(2020, 10, 17), 2020, 5781),
        ("2020-10-17", TrimesterType.SECOND_TRIMESTER, datetime(2020, 12, 10), datetime(2020, 12, 12), 2020, 5781),
        ("2020-11-30", TrimesterType.SECOND_TRIMESTER, datetime(2020, 12, 10), datetime(2020, 12, 12), 2020, 5781),
        ("2020-12-01", TrimesterType.SECOND_TRIMESTER, datetime(2020, 12, 10), datetime(2020, 12, 12), 2020, 5781),
        ("2020-12-10", TrimesterType.SECOND_TRIMESTER, datetime(2020, 12, 10), datetime(2020, 12, 12), 2020, 5781),
        ("2020-12-11", TrimesterType.SECOND_TRIMESTER, datetime(2020, 12, 10), datetime(2020, 12, 12), 2020, 5781),
        ("2020-12-12", TrimesterType.THIRD_TRIMESTER, datetime(2021, 4, 20), datetime(2021, 4, 22), 2020, 5781),
        ("2021-01-01", TrimesterType.THIRD_TRIMESTER, datetime(2021, 4, 20), datetime(2021, 4, 22), 2020, 5781),
        ("2021-03-01", TrimesterType.THIRD_TRIMESTER, datetime(2021, 4, 20), datetime(2021, 4, 22), 2020, 5781),
        ("2021-03-31", TrimesterType.THIRD_TRIMESTER, datetime(2021, 4, 20), datetime(2021, 4, 22), 2020, 5781),
        ("2021-04-01", TrimesterType.THIRD_TRIMESTER, datetime(2021, 4, 20), datetime(2021, 4, 22), 2020, 5781),
        ("2021-04-20", TrimesterType.THIRD_TRIMESTER, datetime(2021, 4, 20), datetime(2021, 4, 22), 2020, 5781),
        ("2021-04-21", TrimesterType.THIRD_TRIMESTER, datetime(2021, 4, 20), datetime(2021, 4, 22), 2020, 5781),
        ("2021-04-22", TrimesterType.NULL_TRIMESTER, None, None, 2020, 5781),
        ("2021-07-01", TrimesterType.NULL_TRIMESTER, None, None, 2020, 5781),
        ("2021-07-20", TrimesterType.NULL_TRIMESTER, None, None, 2020, 5781),
        ("2021-08-20", TrimesterType.NULL_TRIMESTER, None, None, 2020, 5781),
        ("2021-09-01", TrimesterType.FIRST_TRIMESTER, datetime(2021, 10, 15), datetime(2021, 10, 17), 2021, 5782)
    ])
def test_get_current_year_and_trimester_config1(current_date, expected_trimester_name,
                                                expected_meeting_end_of_trimester,
                                                expected_actual_end_of_trimester, expected_gregorian_school_year,
                                                expected_hebrew_school_year):
    with freeze_time(current_date):
        trimester = get_current_trimester()
        assert trimester.name == expected_trimester_name
        assert trimester.meeting_end_of_trimester == expected_meeting_end_of_trimester
        assert trimester.actual_end_of_trimester == expected_actual_end_of_trimester
        assert trimester.gregorian_school_year == expected_gregorian_school_year
        assert trimester.hebrew_school_year == expected_hebrew_school_year


@patch('utils.school_dates.STUDENT_MEETING_DATES', trimester_config2)
@patch('utils.school_dates.GRACE_PERIOD', 2)
@pytest.mark.parametrize(
    "current_date, expected_trimester_name, expected_meeting_end_of_trimester, "
    "expected_actual_end_of_trimester, expected_gregorian_school_year, expected_hebrew_school_year",
    [
        ("2021-04-30", TrimesterType.THIRD_TRIMESTER, datetime(2021, 5, 1), datetime(2021, 5, 3), 2020, 5781),
        ("2021-05-01", TrimesterType.THIRD_TRIMESTER, datetime(2021, 5, 1), datetime(2021, 5, 3), 2020, 5781),
        ("2021-05-03", TrimesterType.NULL_TRIMESTER, None, None, 2020, 5781),
        ("2021-05-30", TrimesterType.NULL_TRIMESTER, None, None, 2020, 5781),
        ("2021-06-30", TrimesterType.NULL_TRIMESTER, None, None, 2020, 5781),
        ("2021-07-01", TrimesterType.NULL_TRIMESTER, None, None, 2020, 5781),
        ("2021-07-31", TrimesterType.NULL_TRIMESTER, None, None, 2020, 5781),
        ("2021-08-01", TrimesterType.NULL_TRIMESTER, None, None, 2020, 5781),
        ("2021-08-31", TrimesterType.NULL_TRIMESTER, None, None, 2020, 5781),
        ("2021-09-01", TrimesterType.FIRST_TRIMESTER, datetime(2021, 11, 14), datetime(2021, 11, 16), 2021, 5782),
        ("2021-10-15", TrimesterType.FIRST_TRIMESTER, datetime(2021, 11, 14), datetime(2021, 11, 16), 2021, 5782),
        ("2021-11-14", TrimesterType.FIRST_TRIMESTER, datetime(2021, 11, 14), datetime(2021, 11, 16), 2021, 5782),
        ("2021-11-16", TrimesterType.SECOND_TRIMESTER, datetime(2022, 1, 2), datetime(2022, 1, 4), 2021, 5782),
        ("2021-11-30", TrimesterType.SECOND_TRIMESTER, datetime(2022, 1, 2), datetime(2022, 1, 4), 2021, 5782),
        ("2021-12-01", TrimesterType.SECOND_TRIMESTER, datetime(2022, 1, 2), datetime(2022, 1, 4), 2021, 5782),
        ("2022-01-01", TrimesterType.SECOND_TRIMESTER, datetime(2022, 1, 2), datetime(2022, 1, 4), 2021, 5782),
        ("2022-03-01", TrimesterType.THIRD_TRIMESTER, datetime(2022, 5, 1), datetime(2022, 5, 3), 2021, 5782),
        ("2022-03-31", TrimesterType.THIRD_TRIMESTER, datetime(2022, 5, 1), datetime(2022, 5, 3), 2021, 5782),
        ("2022-04-01", TrimesterType.THIRD_TRIMESTER, datetime(2022, 5, 1), datetime(2022, 5, 3), 2021, 5782),
        ("2022-04-30", TrimesterType.THIRD_TRIMESTER, datetime(2022, 5, 1), datetime(2022, 5, 3), 2021, 5782),
        ("2022-05-01", TrimesterType.THIRD_TRIMESTER, datetime(2022, 5, 1), datetime(2022, 5, 3), 2021, 5782),
        ("2022-05-03", TrimesterType.NULL_TRIMESTER, None, None, 2021, 5782),
        ("2022-07-01", TrimesterType.NULL_TRIMESTER, None, None, 2021, 5782),
        ("2022-07-20", TrimesterType.NULL_TRIMESTER, None, None, 2021, 5782),
        ("2022-08-20", TrimesterType.NULL_TRIMESTER, None, None, 2021, 5782),
        ("2022-09-01", TrimesterType.FIRST_TRIMESTER, datetime(2022, 11, 14), datetime(2022, 11, 16), 2022, 5783),
        ("2022-09-20", TrimesterType.FIRST_TRIMESTER, datetime(2022, 11, 14), datetime(2022, 11, 16), 2022, 5783)
    ])
def test_get_current_year_and_trimester_config2(current_date, expected_trimester_name,
                                                expected_meeting_end_of_trimester,
                                                expected_actual_end_of_trimester, expected_gregorian_school_year,
                                                expected_hebrew_school_year):
    with freeze_time(current_date):
        trimester = get_current_trimester()
        assert trimester.name == expected_trimester_name
        assert trimester.meeting_end_of_trimester == expected_meeting_end_of_trimester
        assert trimester.actual_end_of_trimester == expected_actual_end_of_trimester
        assert trimester.gregorian_school_year == expected_gregorian_school_year
        assert trimester.hebrew_school_year == expected_hebrew_school_year


def test_get_current_year_and_trimester_no_mock():
    trimester = get_current_trimester()
    assert isinstance(trimester.name, TrimesterType)
    assert isinstance(trimester.meeting_end_of_trimester, datetime)
    assert isinstance(trimester.actual_end_of_trimester, datetime)
    assert isinstance(trimester.gregorian_school_year, int)


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
        assert get_gregorian_school_year(datetime.now()) == expected_start_of_school


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
        assert get_year_of_trimester(trimester_start) == expected_start_of_school


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
        assert get_year_of_trimester(trimester_start) == expected_start_of_school


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
        assert get_year_of_trimester(trimester_start) == expected_start_of_school
