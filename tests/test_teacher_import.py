import io

import pytest

from evaluations.roster_import import hash_ministry_id
from evaluations.teacher_import import (
    DbTeacher, TeachersFileError, TeacherFileRow, TeacherToCreate, plan_teacher_import, read_teachers_file,
)


def file_row(row_number, external_id, first_name, last_name, is_homeroom=False):
    return TeacherFileRow(row_number, external_id, first_name, last_name, '', is_homeroom)


def db_teacher(teacher_id, first_name, last_name, external_id=None, is_deleted=False, is_superuser=False,
               is_homeroom=None):
    return DbTeacher(teacher_id, first_name, last_name, external_id, is_deleted, is_superuser, is_homeroom)


def test_plan():
    db_teachers = [
        db_teacher(1, 'דנה', 'כהן', external_id='h1'),  # Still teaching
        db_teacher(2, 'רון', 'לוי', external_id='h2', is_deleted=True),  # Came back
        db_teacher(3, 'יעל', 'בר', external_id='h3'),  # Left
        db_teacher(4, 'נועם', 'שקד'),  # Never linked, left
        db_teacher(5, 'אלון', 'אביב', is_superuser=True),  # Admin, not in the file
        db_teacher(6, 'גל', 'עוז', external_id='h6', is_deleted=True),  # Left long ago
    ]
    file_rows = [
        file_row(2, 'h1', 'דנה', 'כהן-לוי'),  # A different spelling doesn't matter
        file_row(3, 'h2', 'רון', 'לוי'),
        file_row(4, 'h7', 'מיכל', 'אדיבי'),
    ]
    plan = plan_teacher_import(file_rows, db_teachers)

    assert [t.id for t in plan.teachers_to_keep] == [1]
    assert [t.id for t in plan.teachers_to_restore] == [2]
    assert plan.teachers_to_create == [TeacherToCreate('מיכל', 'אדיבי', 'h7')]
    assert [t.id for t in plan.teachers_to_soft_delete] == [3, 4]
    assert plan.homeroom_changes == plan.errors == []


def test_second_run_changes_nothing():
    plan = plan_teacher_import([file_row(2, 'h1', 'דנה', 'כהן')], [db_teacher(1, 'דנה', 'כהן', external_id='h1')])
    assert len(plan.teachers_to_keep) == 1
    assert plan.teachers_to_restore == plan.teachers_to_create == plan.teachers_to_soft_delete == plan.errors == []


@pytest.mark.parametrize("file_rows, db_teachers, message", [
    ([file_row(2, 'h1', 'דנה', 'כהן'), file_row(3, 'h1', 'רון', 'לוי')], [], "same ת.ז. as an earlier row"),
    ([file_row(2, 'h1', 'דנה', 'כהן')], [db_teacher(7, 'דנה', 'כהן', is_deleted=True)], "already belongs to teacher 7"),
    ([file_row(2, 'h1', 'דנה', 'כהן'), file_row(3, 'h2', 'דנה', 'כהן')], [],
     "already belongs to the new teacher on row 2"),
    ([file_row(2, 'h1', 'א' * 21, 'כהן')], [], "longer than 20"),
])
def test_plan_errors(file_rows, db_teachers, message):
    plan = plan_teacher_import(file_rows, db_teachers)
    assert any(message in error for error in plan.errors), plan.errors


def test_homeroom_changes():
    db_teachers = [
        db_teacher(1, 'דנה', 'כהן', external_id='h1', is_homeroom=False),  # Becomes a homeroom teacher
        db_teacher(2, 'רון', 'לוי', external_id='h2', is_homeroom=True),  # Stops being one
        db_teacher(3, 'יעל', 'בר', external_id='h3', is_homeroom=True),  # Stays one
        db_teacher(4, 'גל', 'עוז', external_id='h4'),  # No account yet: registration sets it
    ]
    file_rows = [file_row(2, 'h1', 'דנה', 'כהן', is_homeroom=True), file_row(3, 'h2', 'רון', 'לוי'),
                 file_row(4, 'h3', 'יעל', 'בר', is_homeroom=True), file_row(5, 'h4', 'גל', 'עוז', is_homeroom=True)]
    plan = plan_teacher_import(file_rows, db_teachers)
    assert [(change.teacher.id, change.is_homeroom) for change in plan.homeroom_changes] == [(1, True), (2, False)]


def csv_file(*lines):
    return io.BytesIO('\n'.join(lines).encode('utf-8'))


HEADER = 'שם ,שם משפחה ,ת.ז,כתובת ,נייד ,מייל ,תפקיד,חונכ/ת'


def test_read_teachers_file_reads_only_teachers_and_the_needed_columns():
    file = csv_file(HEADER,
                    'אבישי , דדון- רווה,18,כפר סבא,054, Avi@Example.com,מורה,כן',
                    'מיכל,אדיבי,000000026,,,,מורה ',
                    'יעל,לוי,,,,,משלבת,כן',  # Not a teacher: skipped, so a missing ת.ז. doesn't matter
                    'אלי,שמחי,,,,,שומר,',
                    'רון,כהן,34,,,,מורה מחול,',
                    ',,,,,,,')
    assert read_teachers_file(file, 'salt') == [
        TeacherFileRow(2, hash_ministry_id(18, 'salt'), 'אבישי', 'דדון- רווה', 'avi@example.com', True),
        TeacherFileRow(3, hash_ministry_id(26, 'salt'), 'מיכל', 'אדיבי', '', False),
        TeacherFileRow(6, hash_ministry_id(34, 'salt'), 'רון', 'כהן', '', False)]


def test_read_teachers_file_with_a_byte_order_mark():
    file = io.BytesIO(('﻿' + HEADER + '\nדנה,כהן,18,,,,מורה,').encode('utf-8'))
    assert [row.first_name for row in read_teachers_file(file, 'salt')] == ['דנה']


@pytest.mark.parametrize("lines, message", [
    (['שם,שם משפחה,ת.ז,תפקיד'], 'first row must have'),
    ([HEADER, 'דנה,,18,,,,מורה,'], 'Row 2: missing'),
    ([HEADER, 'דנה,כהן,,,,,מורה,'], 'Row 2: ת.ז.'),
])
def test_read_teachers_file_errors(lines, message):
    with pytest.raises(TeachersFileError, match=message):
        read_teachers_file(csv_file(*lines), 'salt')


def test_read_teachers_file_rejects_files_that_arent_utf8():
    with pytest.raises(TeachersFileError, match='CSV UTF-8'):
        read_teachers_file(io.BytesIO('שם,שם משפחה'.encode('cp1255')), 'salt')
