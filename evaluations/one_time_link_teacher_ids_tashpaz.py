"""
ONE-TIME, for the first teacher import (תשפ״ז): run before that upload. From the repo root:
    python -m evaluations.one_time_link_teacher_ids_tashpaz <teachers file>

Links the existing teachers, soft-deleted ones included, to their row in the teachers file by setting their external_id,
and changes nothing else (the upload then restores a linked soft-deleted teacher). A teacher is linked when their
first and last name are the same as exactly one row of the file, or when the email of their account is the email on
exactly one row. It prints every link and whoever stays unlinked on either side. For
a teacher who should be linked but isn't, fix their name in the admin to match the file and run it again: it only
looks at teachers that don't have an id yet. The upload on /evaluations/import_teachers then creates the unlinked rows
and soft-deletes the unlinked teachers.
"""
import getpass
import os
import sys
from collections import defaultdict

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'profile_server.settings')
django.setup()

from django.conf import settings  # noqa: E402
from django.db import transaction  # noqa: E402

from accounts.models import TeacherUser  # noqa: E402
from evaluations.models import Teacher  # noqa: E402
from evaluations.teacher_import import read_teachers_file  # noqa: E402

with open(sys.argv[1], 'rb') as f:
    file_rows = read_teachers_file(f, getpass.getpass("Password for the teachers file (Enter if none): "),
                                 settings.STUDENT_ID_SALT)
db_teachers = list(Teacher.objects_with_deleted.filter(external_id__isnull=True))
emails = {user.teacher_object_id: user.email.lower() for user in TeacherUser.objects.exclude(teacher_object=None)}
linked_ids = set(Teacher.objects_with_deleted.exclude(external_id=None).values_list('external_id', flat=True))
file_rows = [file_row for file_row in file_rows if file_row.external_id not in linked_ids]

file_rows_by_name, file_rows_by_email = defaultdict(list), defaultdict(list)
for file_row in file_rows:
    file_rows_by_name[(file_row.first_name, file_row.last_name)].append(file_row)
    if file_row.email:
        file_rows_by_email[file_row.email].append(file_row)

links = {}  # teacher id -> (file row, how)
for teacher in db_teachers:
    by_name = file_rows_by_name.get((teacher.first_name, teacher.last_name), [])
    by_email = file_rows_by_email.get(emails.get(teacher.id), [])
    if len(by_name) == 1:
        links[teacher.id] = (by_name[0], 'name')
    elif len(by_email) == 1:
        links[teacher.id] = (by_email[0], 'email')

linked_rows = [id(file_row) for file_row, _ in links.values()]
problems = ["A row of the file is linked to two teachers"] if len(set(linked_rows)) != len(linked_rows) else []

teachers_by_id = {teacher.id: teacher for teacher in db_teachers}
print("Teachers to link to their row of the file:")
for teacher_id, (file_row, how) in sorted(links.items(), key=lambda link: link[1][0].row_number):
    deleted = ', soft-deleted' if teachers_by_id[teacher_id].is_deleted else ''
    print(f"{teacher_id:>5}  {teachers_by_id[teacher_id]}  <-  '{file_row.name}'  (by {how}{deleted})")

by_name = sum(1 for _, how in links.values() if how == 'name')
print(f"\n{len(links)} teachers to link: {by_name} by name, {len(links) - by_name} by email.")

print("\nActive teachers staying unlinked (the upload soft-deletes them unless their account is a superuser):")
for teacher in db_teachers:
    if teacher.id not in links and not teacher.is_deleted:
        print(f"{teacher.id:>5}  {teacher}")
print("\nRows of the file staying unlinked (the upload creates them as new teachers):")
for file_row in file_rows:
    if id(file_row) not in linked_rows:
        print(f"  row {file_row.row_number}  {file_row.name}")

if problems:
    print("\n".join(["Nothing written:"] + problems))
elif links and input(f"Set the ת.ז. of these {len(links)} teachers? [y/N] ") == 'y':
    with transaction.atomic():
        for teacher_id, (file_row, _) in links.items():
            teacher = teachers_by_id[teacher_id]
            teacher.external_id = file_row.external_id
            teacher.save(update_fields=['external_id'])
    print(f"Done: {len(links)} teachers have their ת.ז.")
else:
    print("Nothing written")
