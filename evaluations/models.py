from django.db.models import CharField, ForeignKey, ManyToManyField, Model, DO_NOTHING, SmallIntegerField, TextField


class Teacher(Model):
    first_name = CharField(max_length=20)
    last_name = CharField(max_length=30)

    class Meta:
        unique_together = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Subject(Model):
    subject_name = CharField(max_length=100, unique=True)

    def __str__(self):
        return self.subject_name


class House(Model):
    house_name = CharField(max_length=20, unique=True)

    def __str__(self):
        return self.house_name


class Class(Model):
    name = CharField(max_length=100, unique=True)
    subject = ForeignKey(Subject, on_delete=DO_NOTHING)
    house = ForeignKey(House, on_delete=DO_NOTHING)

    class Meta:
        verbose_name_plural = "Classes"

    def __str__(self):
        return self.name


class Student(Model):
    first_name = CharField(max_length=20)
    last_name = CharField(max_length=30)
    homeroom_teacher = ForeignKey(Teacher, on_delete=DO_NOTHING)
    classes = ManyToManyField(Class)
    house = ForeignKey(House, on_delete=DO_NOTHING)

    class Meta:
        unique_together = ['first_name', 'last_name', 'house']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Evaluation(Model):
    student = ForeignKey(Student, on_delete=DO_NOTHING)
    evaluated_class = ForeignKey(Class, on_delete=DO_NOTHING)
    trimester = SmallIntegerField(choices=((1, 'First meeting'), (2, 'Second meeting'), (3, 'Third meeting')))
    evaluation_text = TextField()

    class Meta:
        unique_together = ['student', 'evaluated_class', 'trimester']
