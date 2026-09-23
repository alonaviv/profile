import io

import openpyxl
import pytest

from evaluations.roster_import import (
    DbStudent, MinistryFileError, MinistryRow, StudentToCreate, hash_ministry_id, house_for_grade, is_valid_israeli_id,
    normalize_ministry_id, plan_import, read_ministry_file, split_ministry_name,
)


def ministry_row(row_number, external_id, name, grade="ג' - 1"):
    return MinistryRow(row_number, external_id, name, grade)


def db_student(student_id, first_name, last_name, house='חט״צ', external_id=None, is_deleted=False):
    return DbStudent(student_id, first_name, last_name, house, external_id, is_deleted)


@pytest.mark.parametrize("grade, house", [
    ("א' - 1", 'חט״צ'), ("ב' - 2", 'חט״צ'), ("ג' - 1", 'צעירי יסודי'), ("ד' - 1", 'צעירי יסודי'),
    ("ה' - 1", 'בוגרי יסודי'), ("ו' - 1", 'בוגרי יסודי'), ("ז' - 1", 'חט״ב'), ("ט' - 3", 'חט״ב'),
    ("י' - 1", 'חט״ע'), ("יא'' - 1", 'חט״ע'), ("יב'' - 3", 'חט״ע'), ("יב׳׳ - 3", 'חט״ע'), ('יא" - 2', 'חט״ע'),
])
def test_house_for_grade(grade, house):
    assert house_for_grade(grade) == house


@pytest.mark.parametrize("grade", ["", None, "יג' - 1", "גן - 1", "1"])
def test_house_for_unknown_grade(grade):
    with pytest.raises(ValueError):
        house_for_grade(grade)


def test_ministry_id_normalization():
    assert normalize_ministry_id(12345678) == normalize_ministry_id('012345678') == \
        normalize_ministry_id(' 12345678 ') == normalize_ministry_id(12345678.0) == '12345678'
    for bad in ('12a', '', None, '1234567890', '000000000', 1.5):
        with pytest.raises(ValueError):
            normalize_ministry_id(bad)


def test_hash_is_salted_and_ignores_leading_zeros():
    assert hash_ministry_id(12345678, 'salt') == hash_ministry_id('012345678', 'salt')
    assert hash_ministry_id(12345678, 'salt') != hash_ministry_id(12345678, 'pepper')
    assert '12345678' not in hash_ministry_id(12345678, 'salt')
    assert len(hash_ministry_id(12345678, 'salt')) == 64


def test_israeli_id_check_digit():
    assert is_valid_israeli_id('000000018')
    assert is_valid_israeli_id('18')
    assert is_valid_israeli_id('123456782')
    assert not is_valid_israeli_id('123456789')


@pytest.mark.parametrize("full_name, expected", [
    ("זלפוגה עמנואל", ('עמנואל', 'זלפוגה')),
    ("בן יהודה אורי", ('אורי', 'בן יהודה')),
    ("זוסמן דויד בנימין", ('בנימין', 'זוסמן דויד')),
])
def test_split_ministry_name(full_name, expected):
    assert split_ministry_name(full_name) == expected


def test_plan():
    db_students = [
        db_student(1, 'דוידי', 'זוסמן', external_id='h1', house='צעירי יסודי'),
        db_student(2, 'יעל', 'לוי', external_id='h2', is_deleted=True),  # Came back
        db_student(3, 'רון', 'עוזרי', external_id='h3'),  # Left
        db_student(4, 'נועה', 'בר'),  # Never had an id, left
        db_student(5, 'דן', 'כהן', external_id='h5', is_deleted=True),  # Left long ago
    ]
    ministry_rows = [
        ministry_row(2, 'h1', 'זוסמן דויד בנימין', "ה' - 1"),
        ministry_row(3, 'h2', 'לוי יעל'),
        ministry_row(4, 'h4', 'חדש נועם אלי', "א' - 1"),
    ]
    plan = plan_import(ministry_rows, db_students)

    assert [(m.db_student.id, m.new_house) for m in plan.students_to_update] == [
        (1, 'בוגרי יסודי'), (2, 'צעירי יסודי')]
    assert [m.db_student.id for m in plan.restored_students] == [2]
    assert [m.db_student.id for m in plan.house_changes] == [1, 2]
    assert plan.students_to_create == [
        StudentToCreate('אלי', 'חדש נועם', 'חט״צ', "א' - 1", 'h4', 'חדש נועם אלי')]
    assert [s.id for s in plan.students_to_soft_delete] == [3, 4]
    assert plan.errors == []


def test_second_run_changes_nothing():
    db_students = [db_student(1, 'דן', 'כהן', external_id='h1', house='צעירי יסודי')]
    plan = plan_import([ministry_row(2, 'h1', 'כהן דן')], db_students)
    assert len(plan.students_to_update) == 1
    assert plan.house_changes == plan.students_to_create == plan.students_to_soft_delete == plan.errors == []


@pytest.mark.parametrize("ministry_rows, db_students, message", [
    ([ministry_row(2, 'h1', 'כהן דן'), ministry_row(3, 'h1', 'לוי יעל')], [], "same ת.ז. as an earlier row"),
    ([ministry_row(2, 'h1', 'כהן דן', "גן - 1")], [], "Unrecognised grade"),
    ([ministry_row(2, 'h1', 'כהן')], [], "Can't split"),
    ([ministry_row(2, 'h1', 'כהן דן')], [db_student(7, 'דן', 'כהן', is_deleted=True)], "already exists (id 7)"),
    ([ministry_row(2, 'h1', 'כהן דן'), ministry_row(3, 'h2', 'כהן דן')], [], "already exists (id new, row 2)"),
])
def test_plan_errors(ministry_rows, db_students, message):
    plan = plan_import(ministry_rows, db_students)
    assert any(message in error for error in plan.errors), plan.errors


def xlsx(*sheet_rows):
    workbook = openpyxl.Workbook()
    for sheet_row in sheet_rows:
        workbook.active.append(sheet_row)
    content = io.BytesIO()
    workbook.save(content)
    content.seek(0)
    return content


def test_read_ministry_file_reads_only_the_three_columns():
    file = xlsx(['שם רשמי', 'טלפון', 'ת.ז. תלמיד', 'כיתת אם', 'שם תלמיד ', 'ת.לידה'],
                ['כהן דן', '050', 18, "א' - 1", ' כהן  דן ', '2019'],
                [None, None, None, None, None, None],
                ['לוי יעל', '052', '000000026', "יא'' - 2", 'לוי יעל', '2009'])
    assert read_ministry_file(file, None, 'salt') == [
        MinistryRow(2, hash_ministry_id(18, 'salt'), 'כהן דן', "א' - 1"),
        MinistryRow(4, hash_ministry_id(26, 'salt'), 'לוי יעל', "יא'' - 2")]


@pytest.mark.parametrize("sheet_rows, message", [
    ([['כותרת'], ['ת.ז. תלמיד', 'כיתת אם', 'שם תלמיד']], 'first row must have'),
    ([['ת.ז. תלמיד', 'כיתת אם', 'שם תלמיד'], [18, None, 'כהן דן']], 'Row 2: missing'),
    ([['ת.ז. תלמיד', 'כיתת אם', 'שם תלמיד'], ['12a', "א' - 1", 'כהן דן']], 'Row 2: ת.ז.'),
])
def test_read_ministry_file_errors(sheet_rows, message):
    with pytest.raises(MinistryFileError, match=message):
        read_ministry_file(xlsx(*sheet_rows), None, 'salt')


def test_read_ministry_file_rejects_other_files():
    with pytest.raises(MinistryFileError, match="Can't read"):
        read_ministry_file(io.BytesIO(b'not a spreadsheet'), None, 'salt')
