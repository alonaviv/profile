import io

import openpyxl
import pytest

from evaluations.roster_import import hash_ministry_id
from evaluations.teacher_import import (
    DbTeacher, TeachersFileError, TeacherFileRow, TeacherToCreate, plan_teacher_import, read_teachers_file,
)


def file_row(row_number, external_id, first_name, last_name):
    return TeacherFileRow(row_number, external_id, first_name, last_name, '')


def db_teacher(teacher_id, first_name, last_name, external_id=None, is_deleted=False, is_superuser=False):
    return DbTeacher(teacher_id, first_name, last_name, external_id, is_deleted, is_superuser)


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
    assert plan.errors == []


def test_second_run_changes_nothing():
    plan = plan_teacher_import([file_row(2, 'h1', 'דנה', 'כהן')], [db_teacher(1, 'דנה', 'כהן', external_id='h1')])
    assert len(plan.teachers_to_keep) == 1
    assert plan.teachers_to_restore == plan.teachers_to_create == plan.teachers_to_soft_delete == plan.errors == []


@pytest.mark.parametrize("file_rows, db_teachers, message", [
    ([file_row(2, 'h1', 'דנה', 'כהן'), file_row(3, 'h1', 'רון', 'לוי')], [], "same ת.ז. as an earlier row"),
    ([file_row(2, 'h1', 'דנה', 'כהן')], [db_teacher(7, 'דנה', 'כהן', is_deleted=True)], "already belongs to teacher 7"),
    ([file_row(2, 'h1', 'דנה', 'כהן'), file_row(3, 'h2', 'דנה', 'כהן')], [], "already belongs to the new teacher on row 2"),
    ([file_row(2, 'h1', 'א' * 21, 'כהן')], [], "longer than 20"),
])
def test_plan_errors(file_rows, db_teachers, message):
    plan = plan_teacher_import(file_rows, db_teachers)
    assert any(message in error for error in plan.errors), plan.errors


def xlsx(*sheet_rows):
    workbook = openpyxl.Workbook()
    for sheet_row in sheet_rows:
        workbook.active.append(sheet_row)
    content = io.BytesIO()
    workbook.save(content)
    content.seek(0)
    return content


def test_read_teachers_file_reads_only_the_needed_columns():
    file = xlsx([None, 'שם ', 'שם משפחה ', 'ת.ז', 'כתובת ', 'נייד ', 'מייל ', 'תפקיד'],
                [None, 'אבישי ', 'דדון- רווה', 18, 'כפר סבא', '054', ' Avi@Example.com', 'מורה'],
                [None, None, None, None, None, None, None, None],
                [None, 'מיכל', 'אדיבי', '000000026', '', '', None, 'מורה'])
    assert read_teachers_file(file, None, 'salt') == [
        TeacherFileRow(2, hash_ministry_id(18, 'salt'), 'אבישי', 'דדון- רווה', 'avi@example.com'),
        TeacherFileRow(4, hash_ministry_id(26, 'salt'), 'מיכל', 'אדיבי', '')]


@pytest.mark.parametrize("sheet_rows, message", [
    ([['שם', 'שם משפחה']], 'first row must have'),
    ([['שם', 'שם משפחה', 'ת.ז'], ['דנה', None, 18]], 'Row 2: missing'),
    ([['שם', 'שם משפחה', 'ת.ז'], ['דנה', 'כהן', None]], 'Row 2: ת.ז.'),
])
def test_read_teachers_file_errors(sheet_rows, message):
    with pytest.raises(TeachersFileError, match=message):
        read_teachers_file(xlsx(*sheet_rows), None, 'salt')
