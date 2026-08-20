from django.shortcuts import render
from django.db.models import Avg
from .models import Student, Course, Grade


def dashboard_view(request):
    return render(request, "dashboard.html")


def students_view(request):
    students = Student.objects.all()  # Holt alle Studenten aus der Datenbank
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
