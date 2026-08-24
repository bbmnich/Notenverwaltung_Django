from django.contrib import admin
from django.urls import path
from basis import views  # Importiert Views aus der App

urlpatterns = [
    path("admin/", admin.site.urls),  # Standard-Django-Admin
    path("", views.dashboard_view, name="dashboard"),
    path("students/", views.students_view, name="students"),
    path("courses/", views.courses_view, name="courses"),
    path("grades/", views.grades_view, name="grades"),
    path("reports/", views.reports_view, name="reports"),
    path("admin-bereich/", views.admin_bereich_view, name="admin_bereich"),
    path('reports/', views.reports_view, name='reports'),
    path('students/new/', views.student_create_view, name='student_create'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
]
