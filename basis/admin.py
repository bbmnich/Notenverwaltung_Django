from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Course, Grade, Student

admin.site.site_header = "Schuladministration"
admin.site.site_title = "Schuladministration"
admin.site.index_title = "Willkommen im Verwaltungsbereich"

# Mit ImportExportModel Admin
admin.site.register(Student, ImportExportModelAdmin)
admin.site.register(Course, ImportExportModelAdmin)
admin.site.register(Grade, ImportExportModelAdmin)