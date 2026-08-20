from django.contrib import admin
from .models import Student, Course, Grade

admin.site.site_header = "Schuladministration"
admin.site.site_title = "Schuladministration"
admin.site.index_title = "Willkommen im Verwaltungsbereich"

admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Grade)
