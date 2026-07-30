from django.contrib import admin
from .models import Student, Course, Grade

admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Grade)
