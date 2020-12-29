from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, reverse, HttpResponse

from class_manager.forms import ClassForm, AddStudentsForm
from evaluations.models import Class, Student, House
from evaluations.views import populate_evaluations_in_teachers_classes
from utils.school_dates import get_current_trimester

"""
Every view in the site needs to pass the teacher object in the context, so it can display the name
of the logged in teacher in the navbar. Get it from the function get_teacher_object
"""


# Managing Classes

@login_required
def manage_classes(request):
    teacher = request.user
    if teacher:
        classes = teacher.class_set.filter(hebrew_year=get_current_trimester().hebrew_school_year)
    else:
        classes = []

    classes = sorted(classes.all(), key=lambda klass: klass.name)
    context = {'classes': classes, 'teacher': teacher}
    return render(request, 'class_manager/manage_classes.html', context)


@login_required
def manage_students_in_class(request, class_id):
    teacher = request.user
    klass = Class.objects.get(id=class_id)

    if klass.teacher != teacher:
        return HttpResponseForbidden(f"<h1> לא ניתן לערוך את השיעור {klass} שאינכם מלמדים")
    if klass.hebrew_year != get_current_trimester().hebrew_school_year:
        return HttpResponseForbidden(f"<h1> לא ניתן לערוך שיעור של שנה {klass.hebrew_year} </h1>")

    students = sorted(klass.students.all(), key=lambda student: (student.first_name, student.last_name))

    context = {'class': klass, 'students': students, 'teacher': teacher}
    return render(request, 'class_manager/manage_students_in_class.html', context)


@login_required
def delete_student_from_class(request, class_id, student_id):
    teacher = request.user
    klass = Class.objects.get(id=class_id)

    if klass.teacher != teacher:
        return HttpResponseForbidden(f"<h1> לא ניתן לערוך את השיעור {klass} שאינכם מלמדים")
    if klass.hebrew_year != get_current_trimester().hebrew_school_year:
        return HttpResponseForbidden(f"<h1> לא ניתן לערוך שיעור של שנה {klass.hebrew_year} </h1>")

    student = Student.objects.get(id=student_id)

    if klass not in student.classes.all():
        return HttpResponseForbidden(f"<h1> לא קיים רישום של {student} בשיעור {klass} ולכן לא ניתן להסירו")

    klass.students.remove(student)
    populate_evaluations_in_teachers_classes(teacher)

    return redirect(manage_students_in_class, klass.id)


@login_required
def delete_class(request, class_id):
    teacher = request.user
    klass = Class.objects.get(id=class_id)

    if klass.teacher != teacher:
        return HttpResponseForbidden(f"<h1> לא ניתן לערוך את השיעור {klass} שאינכם מלמדים")
    if klass.hebrew_year != get_current_trimester().hebrew_school_year:
        return HttpResponseForbidden(f"<h1> לא ניתן למחוק שיעור של שנה {klass.hebrew_year} </h1>")

    klass.delete()
    return redirect(manage_classes)


@login_required
def add_new_class(request):
    teacher = request.user

    if request.method == "POST":
        form = ClassForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            subject = form.cleaned_data['subject']
            house = form.cleaned_data['house']

            if not Class.objects.filter(name=name, teacher=teacher, hebrew_year=get_current_trimester().hebrew_school_year).exists():
                new_class = Class.objects.create(name=name, subject=subject, house=house, teacher=teacher,
                                                 hebrew_year=get_current_trimester().hebrew_school_year)
                populate_evaluations_in_teachers_classes(teacher)
                return redirect(add_students_to_class, new_class.id)
            else:
                messages.error(request, "השיעור הזה כבר קיים במערכת")

    else:
        form = ClassForm(initial={'house': teacher.house})

    context = {"form": form, "teacher": teacher}
    return render(request, "class_manager/add_new_class.html", context)


@login_required
def edit_class_data(request, class_id):
    teacher = request.user
    klass = Class.objects.get(id=class_id)

    if klass.teacher != teacher:
        return HttpResponse(f"<h1> לא ניתן לערוך את השיעור {klass} שאינכם מלמדים")
    if klass.hebrew_year != get_current_trimester().hebrew_school_year:
        return HttpResponseForbidden(f"<h1> לא ניתן לערוך שיעור של שנה {klass.hebrew_year} </h1>")

    if request.method == "POST":
        form = ClassForm(request.POST, instance=klass)

        if form.is_valid():
            form.save()
            populate_evaluations_in_teachers_classes(teacher)
            return redirect(manage_students_in_class, klass.id)

    else:
        form = ClassForm(instance=klass)

    context = {"form": form, "teacher": teacher, "class": klass}
    return render(request, "class_manager/edit_class_data.html", context)


def add_students_to_class(request, class_id, house_id=None):
    teacher = request.user
    klass = Class.objects.get(id=class_id)

    # The default behavior is to display students from the house that matches the class
    if house_id:
        house = House.objects.get(id=house_id)
    else:
        house = klass.house

    if klass.teacher != teacher:
        return HttpResponse(f"<h1> לא ניתן לערוך את השיעור {klass} שאינכם מלמדים")
    if klass.hebrew_year != get_current_trimester().hebrew_school_year:
        return HttpResponseForbidden(f"<h1> לא ניתן לערוך שיעור של שנה {klass.hebrew_year} </h1>")

    students_to_choose_from = Student.objects.filter(house=house).exclude(classes=klass)

    if request.method == "POST":
        form = AddStudentsForm(request.POST, students=students_to_choose_from)

        if form.is_valid():
            selected_student_ids = form.cleaned_data['students']
            selected_students = []

            for student_id in selected_student_ids:
                student = Student.objects.get(id=student_id)
                selected_students.append(student)

            klass.students.add(*selected_students)
            populate_evaluations_in_teachers_classes(teacher)

            return redirect('manage_students_in_class', class_id)

    else:
        form = AddStudentsForm(students=students_to_choose_from)

    context = {
        "form": form, "teacher": teacher, "class": klass,
        "current_house": house, "houses": House.objects.all()
    }
    return render(request, "class_manager/add_students_to_class.html", context)


# Managing Homeroom
@login_required
def manage_homeroom(request):
    teacher = request.user

    if not teacher.is_homeroom_teacher:
        return redirect(reverse('not_homeroom_teacher_error'))

    context = {'teacher': teacher}
    return render(request, 'class_manager/manage_homeroom.html', context)


@login_required
def add_students_to_homeroom(request, house_id=None):
    teacher = request.user

    if not teacher.is_homeroom_teacher:
        return redirect(reverse('not_homeroom_teacher_error'))

    # The default behavior is to display students from the house that matches the class
    if house_id:
        house = House.objects.get(id=house_id)
    else:
        house = teacher.house

    # Get all students from house that don't already have a homeroom teacher
    students_to_choose_from = Student.objects.filter(homeroom_teacher=None, house=house)

    if request.method == "POST":
        form = AddStudentsForm(request.POST, students=students_to_choose_from)
        if form.is_valid():
            selected_students_ids = form.cleaned_data['students']
            selected_students = []
            for student_id in selected_students_ids:
                student = Student.objects.get(id=student_id)
                selected_students.append(student)
                if student.homeroom_teacher:
                    raise ValueError(f"Cannot add student {student}, as he/she already has a homeroom")

            teacher.student_set.add(*list(selected_students))

            return redirect('manage_homeroom')

    else:
        form = AddStudentsForm(students=students_to_choose_from)

    context = {
        "form": form, "teacher": teacher, "house_of_homeroom": house, "houses": House.objects.all()
    }
    return render(request, "class_manager/add_students_to_homeroom.html", context)


@login_required
def delete_student_from_homeroom(request, student_id):
    teacher = request.user

    if not teacher.is_homeroom_teacher:
        return redirect(reverse('not_homeroom_teacher_error'))

    student = Student.objects.get(id=student_id)
    teacher.student_set.remove(student)

    return redirect(manage_homeroom)
