from django.shortcuts import render

def dashboard_view(request):
    return render(request, 'dashboard.html')

def students_view(request):
    return render(request, 'students.html')

def courses_view(request):
    return render(request, 'courses.html')

def grades_view(request):
    return render(request, 'grades.html')

def reports_view(request):
    return render(request, 'reports.html')

def admin_bereich_view(request):
    return render(request, 'admin_bereich.html')