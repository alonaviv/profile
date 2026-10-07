"""
Yearly teacher list import from the school's teachers file, run from the page /evaluations/import_teachers
(evaluations/teacher_view.py). No Django dependency, so it is unit-tested without a database.

The file is a CSV of the school staff. Only rows whose role (תפקיד) contains "מורה" are teachers who get access;
every other row is skipped. Teachers are keyed on their ת.ז., stored like the students' (Teacher.external_id, a salted
hash, see roster_import). A Teacher record is what lets a person register an account: registration asks for the ת.ז.
and finds the Teacher by it. For every teacher row:
- a teacher with the same external_id is that person, and a soft-deleted one is restored;
- otherwise a new Teacher is created, with the file's first and last name, so they can register;
- the homeroom column (חונכ/ת, "כן" or empty) sets whether their account is a homeroom teacher.
Active teachers that no teacher row matched are soft-deleted and their account is deactivated. Teachers whose account
is a superuser are never touched. Names of existing teachers are never changed.
"""
import csv
import io
from dataclasses import dataclass, field
from typing import List, Optional

from evaluations.roster_import import hash_ministry_id

FIRST_NAME_COLUMN = 'שם'
LAST_NAME_COLUMN = 'שם משפחה'
ID_COLUMN = 'ת.ז'
ROLE_COLUMN = 'תפקיד'
HOMEROOM_COLUMN = 'חונכ/ת'
EMAIL_COLUMN = 'מייל'  # Optional; only the one-time linking script uses it
TEACHER_ROLE = 'מורה'  # A row is a teacher if its role contains this
HOMEROOM_YES = 'כן'


class TeachersFileError(ValueError):
    """A problem reading the uploaded teachers file: shown to the person uploading it."""


@dataclass
class TeacherFileRow:
    """One row read from the teachers file."""
    row_number: int  # Row in the spreadsheet, for messages
    external_id: str  # The row's ת.ז., already hashed
    first_name: str
    last_name: str
    email: str
    is_homeroom: bool

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"


@dataclass
class DbTeacher:
    """A Teacher from the database, soft-deleted ones included."""
    id: int
    first_name: str
    last_name: str
    external_id: Optional[str]
    is_deleted: bool
    is_superuser: bool  # Their account is a superuser
    is_homeroom: Optional[bool]  # Their account's homeroom flag; None if they have no account

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"


@dataclass
class TeacherToCreate:
    """A row of the teachers file whose ת.ז. no DB teacher has. Holds the values the new Teacher gets."""
    first_name: str
    last_name: str
    external_id: str


@dataclass
class HomeroomChange:
    """A teacher whose account's homeroom flag differs from the file's."""
    teacher: DbTeacher
    is_homeroom: bool  # The file's value


@dataclass
class TeacherPlan:
    """What importing the teachers file would do to the DB."""
    teachers_to_keep: List[DbTeacher] = field(default_factory=list)  # Active and in the file: nothing changes
    teachers_to_restore: List[DbTeacher] = field(default_factory=list)  # Soft-deleted and back in the file
    teachers_to_create: List[TeacherToCreate] = field(default_factory=list)
    teachers_to_soft_delete: List[DbTeacher] = field(default_factory=list)  # Active, not in the file, not superusers
    homeroom_changes: List[HomeroomChange] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)  # Any error blocks applying the plan


def read_teachers_file(file, salt):
    """
    Reads the teacher rows of the CSV teachers file: first name, last name, ת.ז., the homeroom column and (if present)
    email. Rows whose role doesn't contain "מורה" are skipped. `file` is a binary file object.
    """
    try:
        text = file.read().decode('utf-8-sig')
    except UnicodeDecodeError:
        raise TeachersFileError("Can't read the file: save it as CSV UTF-8")
    lines = csv.reader(io.StringIO(text))
    headers = [header.strip() for header in next(lines, [])]
    required = (FIRST_NAME_COLUMN, LAST_NAME_COLUMN, ID_COLUMN, ROLE_COLUMN, HOMEROOM_COLUMN)
    if not all(column in headers for column in required):
        raise TeachersFileError(f"The first row must have the columns {', '.join(required)}")
    first_index, last_index, id_index, role_index, homeroom_index = (headers.index(column) for column in required)
    email_index = headers.index(EMAIL_COLUMN) if EMAIL_COLUMN in headers else None

    file_rows = []
    for row_number, values in enumerate(lines, start=2):
        values = [' '.join(value.split()) for value in values] + [''] * len(headers)
        if TEACHER_ROLE not in values[role_index]:
            continue
        try:
            if not values[first_index] or not values[last_index]:
                raise ValueError(f"missing {FIRST_NAME_COLUMN} or {LAST_NAME_COLUMN}")
            email = values[email_index].lower() if email_index is not None else ''
            file_rows.append(TeacherFileRow(row_number, hash_ministry_id(values[id_index], salt), values[first_index],
                                            values[last_index], email, values[homeroom_index] == HOMEROOM_YES))
        except ValueError as e:
            raise TeachersFileError(f"Row {row_number}: {e}")
    return file_rows


def plan_teacher_import(file_rows: List[TeacherFileRow], db_teachers: List[DbTeacher]) -> TeacherPlan:
    """file_rows: every row of the teachers file. db_teachers: every DB teacher, soft-deleted included."""
    plan = TeacherPlan()
    db_teachers_by_external_id = {teacher.external_id: teacher for teacher in db_teachers if teacher.external_id}
    # Who has each name so far: the DB teachers, then the teachers this file creates
    taken_names = {(teacher.first_name, teacher.last_name): f"teacher {teacher.id}" for teacher in db_teachers}
    seen_external_ids = set()
    matched_db_teacher_ids = set()

    for file_row in file_rows:
        label = f"Row {file_row.row_number} '{file_row.name}'"
        if file_row.external_id in seen_external_ids:
            plan.errors.append(f"{label}: same ת.ז. as an earlier row")
            continue
        seen_external_ids.add(file_row.external_id)

        db_teacher = db_teachers_by_external_id.get(file_row.external_id)
        if db_teacher:
            (plan.teachers_to_restore if db_teacher.is_deleted else plan.teachers_to_keep).append(db_teacher)
            matched_db_teacher_ids.add(db_teacher.id)
            if db_teacher.is_homeroom is not None and db_teacher.is_homeroom != file_row.is_homeroom:
                plan.homeroom_changes.append(HomeroomChange(db_teacher, file_row.is_homeroom))
            continue

        if len(file_row.first_name) > 20 or len(file_row.last_name) > 30:
            plan.errors.append(f"{label}: first name longer than 20 characters or last name longer than 30")
        name = (file_row.first_name, file_row.last_name)
        if name in taken_names:
            # Teacher names are unique in the DB, soft-deleted teachers included
            plan.errors.append(f"{label}: this name already belongs to {taken_names[name]}")
        taken_names[name] = f"the new teacher on row {file_row.row_number}"
        plan.teachers_to_create.append(TeacherToCreate(file_row.first_name, file_row.last_name,
                                                       file_row.external_id))

    plan.teachers_to_soft_delete = [teacher for teacher in db_teachers if not teacher.is_deleted
                                    and not teacher.is_superuser and teacher.id not in matched_db_teacher_ids]
    return plan
