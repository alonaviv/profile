"""
Yearly student roster import from the Ministry of Education file (אלפון מלא), run from the page
/evaluations/import_roster (evaluations/roster_view.py). This module has no Django dependency, so it is unit-tested
without a database.

Students are keyed on the ministry student id (ת.ז. תלמיד). The raw id is never stored: Student.external_id holds an
HMAC-SHA256 of it, keyed with the secret settings.STUDENT_ID_SALT (set in profile_server/local_settings.py, which is
not in git). The salt must be backed up together with the database - without it, next year's file can't be matched
to this year's students.

For every row of the file:
- a student with the same external_id is that child: their house and class are updated, and a soft-deleted one is
  restored;
- otherwise it's a new student. The ministry name cell is surname first, so the last word becomes the first name and
  the rest the last name. Names of existing students are never changed.
Active students that no row matched are soft-deleted.
"""
import hashlib
import hmac
import io
import re
from dataclasses import dataclass, field
from typing import List, Optional

import msoffcrypto
import openpyxl
from msoffcrypto.exceptions import InvalidKeyError

ID_COLUMN = 'ת.ז. תלמיד'
GRADE_COLUMN = 'כיתת אם'
NAME_COLUMN = 'שם תלמיד'

GRADE_TO_HOUSE = {
    'א': 'חט״צ', 'ב': 'חט״צ',
    'ג': 'צעירי יסודי', 'ד': 'צעירי יסודי',
    'ה': 'בוגרי יסודי', 'ו': 'בוגרי יסודי',
    'ז': 'חט״ב', 'ח': 'חט״ב', 'ט': 'חט״ב',
    'י': 'חט״ע', 'יא': 'חט״ע', 'יב': 'חט״ע',
}


class MinistryFileError(ValueError):
    pass


def normalize_ministry_id(raw_id):
    """
    The id as digits without leading zeros, so the same ת.ז. always gives the same hash. The ministry file stores
    the ת.ז. as a number, so Excel hands over 12345674 for 012345674, while a person typing it in the admin keeps
    the zero. Both become '12345674'. Raises ValueError for anything that isn't 1-9 digits.
    """
    if isinstance(raw_id, float) and raw_id.is_integer():
        raw_id = int(raw_id)
    text = str(raw_id if raw_id is not None else '').strip()
    if not text.isdigit() or len(text) > 9 or int(text) == 0:
        raise ValueError("ת.ז. must be up to 9 digits")
    return str(int(text))


def is_valid_israeli_id(normalized_id):
    """The ת.ז. check digit."""
    total = 0
    for position, digit in enumerate(normalized_id.zfill(9)):
        product = int(digit) * (1 + position % 2)
        total += product - 9 if product > 9 else product
    return total % 10 == 0


def hash_ministry_id(raw_id, salt):
    return hmac.new(salt.encode('utf-8'), normalize_ministry_id(raw_id).encode('utf-8'), hashlib.sha256).hexdigest()


def house_for_grade(grade):
    """The Hebrew letters before the '-' of כיתת אם: "א' - 1" -> "חט״צ", "יא'' - 1" -> "חט״ע"."""
    letters = re.sub('[^א-ת]', '', str(grade or '').split('-')[0])
    if letters not in GRADE_TO_HOUSE:
        raise ValueError(f"Unrecognised grade: {grade!r}")
    return GRADE_TO_HOUSE[letters]


def split_ministry_name(full_name):
    """
    The ministry name cell is surname first. The last word is the first name and the rest the surname, which is right
    for two-word surnames ("בן יהודה אורי" -> ('אורי', 'בן יהודה')) but wrong for middle names ("זוסמן דויד בנימין"
    -> ('בנימין', 'זוסמן דויד')). On the students of 2026 it matched the school's spelling of 267 of 315 names.
    """
    parts = full_name.rsplit(maxsplit=1)
    if len(parts) < 2:
        raise ValueError(f"Can't split into first and last name: {full_name!r}")
    last_name, first_name = parts
    return first_name, last_name


@dataclass
class MinistryRow:
    """One student row read from the ministry file."""
    row_number: int  # Row in the spreadsheet, for messages
    external_id: str  # The row's ת.ז., already hashed
    name: str  # As written in the file: surname first
    grade: str  # כיתת אם, e.g. "ו' - 1"


@dataclass
class DbStudent:
    """A Student from the database, soft-deleted ones included."""
    id: int
    first_name: str
    last_name: str
    house: str
    external_id: Optional[str]
    is_deleted: bool

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"


@dataclass
class StudentToUpdate:
    """
    A DB student whose ת.ז. is on a ministry row. The import updates their grade and house, and restores them if
    soft-deleted.
    """
    db_student: DbStudent
    ministry_row: MinistryRow
    new_house: str  # From the ministry row's grade


@dataclass
class StudentToCreate:
    """A ministry row whose ת.ז. no DB student has. Holds the values the new DB student gets."""
    first_name: str
    last_name: str
    house: str
    grade: str
    external_id: str
    name_in_ministry_file: str  # Shown in the preview next to the split first/last name


@dataclass
class Plan:
    """What importing the ministry file would do to the DB."""
    students_to_update: List[StudentToUpdate] = field(default_factory=list)
    students_to_create: List[StudentToCreate] = field(default_factory=list)
    students_to_soft_delete: List[DbStudent] = field(default_factory=list)  # Active DB students not in the file
    errors: List[str] = field(default_factory=list)  # Any error blocks applying the plan

    @property
    def restored_students(self):
        return [student for student in self.students_to_update if student.db_student.is_deleted]

    @property
    def house_changes(self):
        return [student for student in self.students_to_update if student.db_student.house != student.new_house]


def read_ministry_file(file, password, salt):
    """
    Reads the columns ת.ז. תלמיד, כיתת אם and שם תלמיד from the first sheet, whose first row holds the headers.
    Every other column is skipped. `file` is a binary file object.
    """
    try:
        office_file = msoffcrypto.OfficeFile(file)
        if office_file.is_encrypted():
            if not password:
                raise MinistryFileError("The file is password-protected")
            office_file.load_key(password=password)
            content = io.BytesIO()
            office_file.decrypt(content)
        else:
            file.seek(0)
            content = io.BytesIO(file.read())
        sheet_rows = openpyxl.load_workbook(content, read_only=True, data_only=True).worksheets[0].iter_rows(
            values_only=True)
        headers = [str(header or '').strip() for header in next(sheet_rows)]
    except InvalidKeyError:
        raise MinistryFileError("Wrong password for the file")
    except MinistryFileError:
        raise
    except Exception:
        raise MinistryFileError("Can't read the file as an Excel file")

    if not all(column in headers for column in (ID_COLUMN, GRADE_COLUMN, NAME_COLUMN)):
        raise MinistryFileError(f"The first row must have the columns {ID_COLUMN}, {GRADE_COLUMN}, {NAME_COLUMN}")
    columns = [headers.index(column) for column in (ID_COLUMN, GRADE_COLUMN, NAME_COLUMN)]

    ministry_rows = []
    for row_number, values in enumerate(sheet_rows, start=2):
        raw_id, grade, name = (values[index] for index in columns)
        if raw_id is None and not grade and not name:
            continue
        try:
            if not grade or not name:
                raise ValueError(f"missing {GRADE_COLUMN} or {NAME_COLUMN}")
            ministry_rows.append(MinistryRow(row_number, hash_ministry_id(raw_id, salt), ' '.join(str(name).split()),
                                             str(grade).strip()))
        except ValueError as e:
            raise MinistryFileError(f"Row {row_number}: {e}")
    return ministry_rows


def plan_import(ministry_rows: List[MinistryRow], db_students: List[DbStudent]) -> Plan:
    """ministry_rows: every student row of the ministry file. db_students: every DB student, soft-deleted included."""
    plan = Plan()
    db_students_by_external_id = {student.external_id: student for student in db_students if student.external_id}
    taken_names = {(student.first_name, student.last_name): student.id for student in db_students}
    seen_external_ids = set()
    db_student_ids_to_update = set()

    for ministry_row in ministry_rows:
        label = f"Row {ministry_row.row_number} '{ministry_row.name}' ({ministry_row.grade})"
        if ministry_row.external_id in seen_external_ids:
            plan.errors.append(f"{label}: same ת.ז. as an earlier row")
            continue
        seen_external_ids.add(ministry_row.external_id)
        try:
            house = house_for_grade(ministry_row.grade)
        except ValueError as e:
            plan.errors.append(f"{label}: {e}")
            continue

        db_student = db_students_by_external_id.get(ministry_row.external_id)
        if db_student:
            plan.students_to_update.append(StudentToUpdate(db_student, ministry_row, house))
            db_student_ids_to_update.add(db_student.id)
            continue

        try:
            first_name, last_name = split_ministry_name(ministry_row.name)
        except ValueError as e:
            plan.errors.append(f"{label}: {e}")
            continue
        if len(first_name) > 30 or len(last_name) > 30:
            plan.errors.append(f"{label}: name longer than 30 characters")
        if (first_name, last_name) in taken_names:
            # Student names are unique in the DB, soft-deleted students included
            plan.errors.append(f"{label}: a student named '{first_name} {last_name}' already exists "
                               f"(id {taken_names[(first_name, last_name)]})")
        taken_names[(first_name, last_name)] = f"new, row {ministry_row.row_number}"
        plan.students_to_create.append(StudentToCreate(first_name, last_name, house, ministry_row.grade,
                                            ministry_row.external_id, ministry_row.name))

    plan.students_to_soft_delete = [student for student in db_students
                                    if not student.is_deleted and student.id not in db_student_ids_to_update]
    return plan
