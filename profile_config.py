"""
Set when the parent-teacher-kid meeting happen throughout the year ("Trimesters")
* First trimester is from the end of the year until the start of the second semester
* Second trimester is from the start of the second semester to the start of the third semester
* Third trimester is from the start of the third semester to the end of the year
"""

from utils.date_helpers import SchoolDay

# First trimester: starts exactly on START_OF_YEAR (Sept 1st)
# Second trimester: Starts after first meeting date + grace period.
# Third trimester: Starts after second meeting date + grace period.
# No trimester: From after third meeting date + grace period, up to the START_OF_YEAR.

STUDENT_MEETING_DATES = {
    "first_meeting": SchoolDay(20, 10),
    "second_meeting": SchoolDay(16, 2),
    "third_meeting": SchoolDay(8, 6),
}

GRACE_PERIOD = 30  # After this number of days after the meeting, the trimester will end and move on to the next.
EVALUATION_DEADLINE_DAYS = 7  # This number of days before the meeting deadline, all evaluations should be written.

MIN_AMOUNT_OF_CLASSES = 2  # Will alert admins for students that have less than this
