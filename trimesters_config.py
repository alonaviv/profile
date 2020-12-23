"""
Set when the parent-teacher-kid meeting happen throughout the year ("Trimesters")
* First trimester is from the end of the year until the start of the second semester
* Second trimester is from the start of the second semester to the start of the third semester
* Third trimester is from the start of the third semester to the end of the year
"""

from utils.date_helpers import SchoolDay


# First trimester: starts exactly on START_OF_YEAR
# Second trimester: Starts after first meeting date + grace period.
# Third trimester: Starts after second meeting date + grace period.
# No trimester: From after third meeting date + grace period, up to the START_OF_YEAR.

STUDENT_MEETING_DATES = {
    "first_meeting": SchoolDay(15, 10),
    "second_meeting": SchoolDay(10, 2),
    "third_meeting": SchoolDay(20, 5),
}

GRACE_PERIOD = 21  # Days
