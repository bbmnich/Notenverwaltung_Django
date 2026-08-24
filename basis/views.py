from django.shortcuts import render
from django.db.models import Avg
from .models import Student, Course, Grade


def dashboard_view(request):
    # Gesamtzahl der jeweiligen Einträge aus der Datenbank ermitteln
    student_count = Student.objects.count()  # Zählt alle Datensätze in der Student-Tabelle
    course_count = Course.objects.count()  # Zählt alle Datensätze in der Course-Tabelle
    grade_count = Grade.objects.count()  # Zählt alle Datensätze in der Grade-Tabelle

    # Dictionary bündelt die Daten, um sie an das HTML-Template zu übergeben
    context = {
        "student_count": student_count,
        "course_count": course_count,
        "grade_count": grade_count,
    }

    # dashboard mit den aktuellen Daten
    return render(request, "dashboard.html", context)


def students_view(request):
    students = Student.objects.all()  # alle Studenten aus der Datenbank
    return render(request, "students.html", {"students": students})


def courses_view(request):
    courses = Course.objects.all()  # Alle Kurse aus der Datenbank
    return render(request, "courses.html", {"courses": courses})


def grades_view(request):
    grades = Grade.objects.all().order_by("student__name")  # Noten abrufen
    return render(request, "grades.html", {"grades": grades})


def reports_view(request):
    return render(request, "reports.html")


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
