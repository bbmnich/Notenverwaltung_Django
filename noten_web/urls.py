from django.contrib import admin
from django.urls import path
from basis import views  # Importiert Views aus der App

urlpatterns = [
    path("admin/", admin.site.urls),  # Standard-Admin
    path("", views.dashboard_view, name="dashboard"),
    # Students URLs
    path("students/", views.students_view, name="students"),
    path("students/new/", views.student_create_view, name="student_create"),
    path("students/<int:pk>/edit/", views.student_edit, name="student_edit"),
    path("students/<int:pk>/delete/", views.student_delete, name="student_delete"),
    # Courses URLs
    path("courses/", views.course_list, name="courses"),
    path("courses/new/", views.course_create, name="course_create"),
    path("courses/<int:pk>/edit/", views.course_edit, name="course_edit"),
    path("courses/<int:pk>/delete/", views.course_delete, name="course_delete"),
    # Grades URLs
    path("grades/", views.grades_view, name="grades"),
    path('grades/new/', views.grade_create, name='grade_create'),
    path('grades/<int:pk>/edit/', views.grade_edit, name='grade_edit'),
    path('grades/<int:pk>/delete/', views.grade_delete, name='grade_delete'),
    # Weitere URLs
    path("reports/", views.reports_view, name="reports"),
    path("admin-bereich/", views.admin_bereich_view, name="admin_bereich"),
    # CSV Import und Export URLs
    path('export/csv/', views.export_grades_csv, name='export_grades_csv'),
    path('import/csv/', views.import_grades_csv, name='import_grades_csv'),
]
