from datetime import datetime

import pytest
from freezegun import freeze_time
from mock import patch

from utils.school_dates import (
    Trimester, get_current_trimester_and_hebrew_year, get_year_start_of_school,
    get_year_of_trimester
)

trimester_config1 = {
    "second_trimester_start_month": 12,
    "third_trimester_start_month": 4,

}

trimester_config2 = {
    "second_trimester_start_month": 1,
    "third_trimester_start_month": 5,
}


@patch('utils.school_dates.TRIMESTERS_CONFIG', trimester_config1)
@pytest.mark.parametrize("current_date, expected_trimester, expected_year",
                         [
                             ("2020-06-30", Trimester.THIRD_TRIMESTER, 5780),
                             ("2020-07-30", Trimester.FIRST_TRIMESTER, 5781),
                             ("2020-08-01", Trimester.FIRST_TRIMESTER, 5781),
                             ("2020-08-31", Trimester.FIRST_TRIMESTER, 5781),
                             ("2020-09-01", Trimester.FIRST_TRIMESTER, 5781),
                             ("2020-11-30", Trimester.FIRST_TRIMESTER, 5781),
                             ("2020-12-01", Trimester.SECOND_TRIMESTER, 5781),
                             ("2021-01-01", Trimester.SECOND_TRIMESTER, 5781),
                             ("2021-03-01", Trimester.SECOND_TRIMESTER, 5781),
                             ("2021-03-31", Trimester.SECOND_TRIMESTER, 5781),
                             ("2021-04-01", Trimester.THIRD_TRIMESTER, 5781),
                             ("2021-07-01", Trimester.FIRST_TRIMESTER, 5782),
                             ("2021-07-20", Trimester.FIRST_TRIMESTER, 5782)
                         ])
def test_get_current_year_and_trimester_config1(current_date, expected_trimester, expected_year):
    with freeze_time(current_date):
        assert get_current_trimester_and_hebrew_year() == (expected_trimester, expected_year)


@patch('utils.school_dates.TRIMESTERS_CONFIG', trimester_config2)
@pytest.mark.parametrize("current_date, expected_trimester, expected_year",
                         [
                             ("2021-04-30", Trimester.SECOND_TRIMESTER, 5781),
                             ("2021-05-30", Trimester.THIRD_TRIMESTER, 5781),
                             ("2021-06-30", Trimester.THIRD_TRIMESTER, 5781),
                             ("2021-07-01", Trimester.FIRST_TRIMESTER, 5782),
                             ("2021-07-31", Trimester.FIRST_TRIMESTER, 5782),
                             ("2021-08-01", Trimester.FIRST_TRIMESTER, 5782),
                             ("2021-08-31", Trimester.FIRST_TRIMESTER, 5782),
                             ("2021-09-01", Trimester.FIRST_TRIMESTER, 5782),
                             ("2021-11-30", Trimester.FIRST_TRIMESTER, 5782),
                             ("2021-12-01", Trimester.FIRST_TRIMESTER, 5782),
                             ("2022-01-01", Trimester.SECOND_TRIMESTER, 5782),
                             ("2022-03-01", Trimester.SECOND_TRIMESTER, 5782),
                             ("2022-03-31", Trimester.SECOND_TRIMESTER, 5782),
                             ("2022-04-01", Trimester.SECOND_TRIMESTER, 5782),
                             ("2022-04-30", Trimester.SECOND_TRIMESTER, 5782),
                             ("2022-05-01", Trimester.THIRD_TRIMESTER, 5782),
                             ("2022-07-01", Trimester.FIRST_TRIMESTER, 5783),
                             ("2022-07-20", Trimester.FIRST_TRIMESTER, 5783),
                             ("2022-08-20", Trimester.FIRST_TRIMESTER, 5783),
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
                             ("2021-06-30", 2020),
                             ("2021-05-30", 2020),
                             ("2021-07-31", 2021),
                             ("2021-08-01", 2021),
                             ("2021-08-31", 2021),
                             ("2021-09-01", 2021),
                             ("2021-11-30", 2021),
                             ("2021-12-01", 2021),
                             ("2022-01-01", 2021),
                             ("2022-03-01", 2021),
                             ("2022-03-31", 2021),
                             ("2022-04-01", 2021),
                             ("2022-04-30", 2021),
                             ("2022-05-01", 2021),
                             ("2022-07-01", 2022),
                             ("2022-07-20", 2022)
                         ])
def test_get_year_start_of_school(current_date, expected_start_of_school):
    with freeze_time(current_date):
        assert get_year_start_of_school(datetime.now()) == expected_start_of_school


@pytest.mark.parametrize("current_date, trimester_start_month, expected_start_of_school",
                         [
                             ("2021-05-30", 8, 2020),
                             ("2021-06-30", 8, 2020),
                             ("2021-07-30", 8, 2021),
                             ("2021-08-01", 8, 2021),
                             ("2021-08-31", 8, 2021),
                             ("2021-09-01", 8, 2021),
                             ("2021-11-30", 8, 2021),
                             ("2021-12-01", 8, 2021),
                             ("2022-01-01", 8, 2021),
                             ("2022-03-01", 8, 2021),
                             ("2022-03-31", 8, 2021),
                             ("2022-04-01", 8, 2021),
                             ("2022-04-30", 8, 2021),
                             ("2022-05-01", 8, 2021),
                             ("2022-07-01", 8, 2022),
                             ("2022-07-20", 8, 2022),
                             ("2022-08-20", 8, 2022),
                             ("2022-09-20", 8, 2022)
                         ])
def test_get_year_of_trimester_start_of_year(current_date, trimester_start_month, expected_start_of_school):
    with freeze_time(current_date):
        assert get_year_of_trimester(datetime.now(), trimester_start_month) == expected_start_of_school


@pytest.mark.parametrize("current_date, trimester_start_month, expected_start_of_school",
                         [
                             ("2021-05-30", 1, 2021),
                             ("2021-06-30", 1, 2021),
                             ("2021-07-30", 1, 2022),
                             ("2021-08-01", 1, 2022),
                             ("2021-08-31", 1, 2022),
                             ("2021-09-01", 1, 2022),
                             ("2021-11-30", 1, 2022),
                             ("2021-12-01", 1, 2022),
                             ("2022-01-01", 1, 2022),
                             ("2022-03-01", 1, 2022),
                             ("2022-03-31", 1, 2022),
                             ("2022-04-01", 1, 2022),
                             ("2022-04-30", 1, 2022),
                             ("2022-05-01", 1, 2022),
                             ("2022-07-01", 1, 2023),
                             ("2022-07-20", 1, 2023),
                             ("2022-08-20", 1, 2023),
                             ("2022-09-20", 1, 2023)
                         ])
def test_get_year_of_trimester_middle_of_year(current_date, trimester_start_month, expected_start_of_school):
    with freeze_time(current_date):
        assert get_year_of_trimester(datetime.now(), trimester_start_month) == expected_start_of_school


@pytest.mark.parametrize("current_date, trimester_start_month, expected_start_of_school",
                         [
                             ("2021-05-30", 6, 2021),
                             ("2021-06-30", 6, 2021),
                             ("2021-07-30", 6, 2022),
                             ("2021-08-01", 6, 2022),
                             ("2021-08-31", 6, 2022),
                             ("2021-09-01", 6, 2022),
                             ("2021-11-30", 6, 2022),
                             ("2021-12-01", 6, 2022),
                             ("2022-01-01", 6, 2022),
                             ("2022-03-01", 6, 2022),
                             ("2022-03-31", 6, 2022),
                             ("2022-04-01", 6, 2022),
                             ("2022-04-30", 6, 2022),
                             ("2022-05-01", 6, 2022),
                             ("2022-07-01", 6, 2023),
                             ("2022-07-20", 6, 2023),
                             ("2022-08-20", 6, 2023),
                             ("2022-09-20", 6, 2023)
                         ])
def test_get_year_of_trimester_end_of_year(current_date, trimester_start_month, expected_start_of_school):
    with freeze_time(current_date):
        assert get_year_of_trimester(datetime.now(), trimester_start_month) == expected_start_of_school

