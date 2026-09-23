"""
ONE-TIME, for the first roster import (תשפ״ז): run once before that upload and never again. From the repo root:
    python -m evaluations.one_time_link_student_ids_tashpaz <ministry file> <mapping file>

Links the existing active students to their row in the ministry file by setting their external_id, and changes nothing
else. A student is linked when:
- the reviewed mapping pairs them with a name in the file (students whose name is spelled differently). The mapping
  has the db student id in column A, the name as in the ministry file in column D, and 'כן' in the last filled column;
- or their name is the same words as exactly one row of the file, in any order, and no other unlinked student has
  those words.
Everyone else is left alone: the upload on /evaluations/import_roster then creates the unlinked rows and soft-deletes
the unlinked students.
"""
import getpass
import os
import sys
from collections import defaultdict

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'profile_server.settings')
django.setup()

import openpyxl  # noqa: E402
from django.conf import settings  # noqa: E402
from django.db import transaction  # noqa: E402

from evaluations.models import Student  # noqa: E402
from evaluations.roster_import import read_ministry_file  # noqa: E402


def name_key(name):
    return tuple(sorted(name.split()))


def mapping_name(name):
    """The mapping sometimes has a space where the ministry file has a hyphen (בן-ארי)."""
    return ' '.join(str(name).replace('-', ' ').split())


ministry_file, mapping_file = sys.argv[1:]
with open(ministry_file, 'rb') as f:
    ministry_rows = read_ministry_file(f, getpass.getpass("Password for the ministry file: "), settings.STUDENT_ID_SALT)
db_students = list(Student.objects.filter(external_id__isnull=True))
db_students_by_id = {student.id: student for student in db_students}
links = {}  # db student id -> ministry row
problems = []

# 1. The reviewed mapping
ministry_rows_by_name = defaultdict(list)
for ministry_row in ministry_rows:
    ministry_rows_by_name[mapping_name(ministry_row.name)].append(ministry_row)
for values in openpyxl.load_workbook(mapping_file, read_only=True).worksheets[0].iter_rows(values_only=True):
    filled = [value for value in values if value not in (None, '')]
    if not filled or str(filled[-1]).strip() != 'כן':
        continue
    named_rows = ministry_rows_by_name.get(mapping_name(values[3]), [])
    if values[0] not in db_students_by_id:
        problems.append(f"Mapping {values[0]}: not an active student without an id")
    elif len(named_rows) != 1:
        problems.append(f"Mapping {values[0]}: '{values[3]}' is on {len(named_rows)} rows of the file")
    else:
        links[values[0]] = named_rows[0]
linked_by_mapping = len(links)

# 2. Same words
linked_rows = {id(ministry_row) for ministry_row in links.values()}
ministry_rows_by_key, db_students_by_key = defaultdict(list), defaultdict(list)
for ministry_row in ministry_rows:
    if id(ministry_row) not in linked_rows:
        ministry_rows_by_key[name_key(ministry_row.name)].append(ministry_row)
for student in db_students:
    if student.id not in links:
        db_students_by_key[name_key(f"{student.first_name} {student.last_name}")].append(student)
for key, key_students in db_students_by_key.items():
    key_rows = ministry_rows_by_key.get(key, [])
    if len(key_students) == 1 and len(key_rows) == 1:
        links[key_students[0].id] = key_rows[0]
    elif key_rows:
        problems.append(f"Ambiguous: {len(key_students)} students and {len(key_rows)} rows named '{key_rows[0].name}'")

if len({id(ministry_row) for ministry_row in links.values()}) != len(links):
    problems.append("A row of the file is linked to two students")

for student_id, ministry_row in sorted(links.items(), key=lambda link: link[1].row_number):
    print(f"{student_id:>5}  {db_students_by_id[student_id]}  <-  '{ministry_row.name}' ({ministry_row.grade})")
print(f"\n{len(links)} students to link: {linked_by_mapping} by the mapping, {len(links) - linked_by_mapping} by name. "
      f"{len(db_students) - len(links)} active students stay unlinked, "
      f"{len(ministry_rows) - len(links)} rows of the file stay unlinked.")

if problems:
    print("\n".join(["Nothing written:"] + problems))
elif input(f"Set the ministry id of these {len(links)} students? [y/N] ") == 'y':
    with transaction.atomic():
        for student_id, ministry_row in links.items():
            student = db_students_by_id[student_id]
            student.external_id = ministry_row.external_id
            student.save(update_fields=['external_id'])
    print(f"Done: {len(links)} students have their ministry id")
else:
    print("Nothing written")
