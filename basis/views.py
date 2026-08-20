from django.shortcuts import render
from .models import Student

def dashboard_view(request):
    return render(request, 'dashboard.html')

def students_view(request):
    students = Student.objects.all()  # Holt alle Studenten aus der Datenbank
    return render(request, 'students.html', {'students': students})

def courses_view(request):
    return render(request, 'courses.html')

def grades_view(request):
    return render(request, 'grades.html')

def reports_view(request):
    return render(request, 'reports.html')

def admin_bereich_view(request):
    return render(request, 'admin_bereich.html')