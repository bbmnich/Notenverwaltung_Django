from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg
from .forms import StudentForm
from .forms import CourseForm
from .models import Student, Course, Grade


def dashboard_view(request):
    # Gesamtzahl der jeweiligen Einträge aus der Datenbank ermitteln
    student_count = Student.objects.count()  # Zählt alle Datensätze in der Student-Tabelle
    course_count = Course.objects.count()  # Zählt alle Datensätze in der Course-Tabelle
    grade_count = Grade.objects.count()  # Zählt alle Datensätze in der Grade-Tabelle

    # Daten zusammenbündeln, um sie an das HTML-Template zu übergeben
    context = {
        "student_count": student_count,
        "course_count": course_count,
        "grade_count": grade_count,
    }

    # dashboard mit den aktuellen Daten
    return render(request, "dashboard.html", context)


def student_create_view(request):
    # Nutzer sendet das Formular
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()  # Speichert den Studenten in der Datenbank
            return redirect("students")  # Leitet  zur Studenten-Liste weiter
    else:
        # Nutzer ruft die Seite auf (GET-Request): Ein leeres Formular anzeigen
        form = StudentForm()

    return render(request, "student_create.html", {"form": form})


def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect("students")
    else:
        form = StudentForm(instance=student)
    return render(request, "student_edit.html", {"form": form, "student": student})


def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.delete()
        return redirect("students")
    return render(request, "student_delete.html", {"student": student})


def students_view(request):
    students = Student.objects.all()  # alle Studenten aus der Datenbank
    return render(request, "students.html", {"students": students})


def course_list(request):
    courses = Course.objects.all()  # Alle Kurse aus der Datenbank
    return render(request, "courses.html", {"courses": courses})


def course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("courses")
    else:
        form = CourseForm()
    return render(request, "course_form.html", {"form": form})


def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect("courses")
    else:
        form = CourseForm(instance=course)
    return render(request, "course_form.html", {"form": form, "course": course})


def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        course.delete()
        return redirect("courses")
    return render(request, "course_delete.html", {"course": course})


def grades_view(request):
    grades = Grade.objects.all().order_by("student__last_name")  # Nach Nachname sortieren
    return render(request, "grades.html", {"grades": grades})


def admin_bereich_view(request):
    return render(request, "admin_bereich.html")


def reports_view(request):
    # Durchschnittsnote pro Student
    student_averages = Student.objects.annotate(avg_score=Avg("grade__score"))

    # Durchschnittsnote pro Kurs
    course_averages = Course.objects.annotate(avg_score=Avg("grade__score"))

    context = {
        "student_averages": student_averages,
        "course_averages": course_averages,
    }
    return render(request, "reports.html", context)
