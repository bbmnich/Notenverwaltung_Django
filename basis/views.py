from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg
from .forms import CourseForm, GradeForm, StudentForm
from .models import Student, Course, Grade
import csv
from django.http import HttpResponse
import io
from django.contrib import messages


def dashboard_view(request):
    # Gesamtzahl der Einträge aus der Datenbank ermitteln
    student_count = Student.objects.count()  # Zählt alle Datensätze in der Student-Tabelle
    course_count = Course.objects.count()  # Zählt alle Datensätze in der Course-Tabelle
    grade_count = Grade.objects.count()  # Zählt alle Datensätze in der Grade-Tabelle

    # Variablen in ein Dictionary verpacken für die Template-Übergabe
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


#   Note erfassen
def grade_create(request):
    if request.method == "POST":
        form = GradeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("grades")
    else:
        form = GradeForm()
    return render(request, "grade_form.html", {"form": form})


#   Note bearbeiten
def grade_edit(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    if request.method == "POST":
        form = GradeForm(request.POST, instance=grade)
        if form.is_valid():
            form.save()
            return redirect("grades")
    else:
        form = GradeForm(instance=grade)
    return render(request, "grade_form.html", {"form": form, "grade": grade})


#   Note löschen (Delete)
def grade_delete(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    if request.method == "POST":
        grade.delete()
        return redirect("grades")
    return render(request, "grade_delete.html", {"grade": grade})


def admin_bereich_view(request):
    return render(request, "admin_bereich.html")


def reports_view(request):
    # Notendurchschnitt pro Student
    students = Student.objects.annotate(avg_score=Avg("grade__score"))

    # Notendurchschnitt pro Kurs
    courses = Course.objects.annotate(avg_score=Avg("grade__score"))

    context = {
        "student_averages": students,
        "course_averages": courses,
    }
    return render(request, "reports.html", context)


# CSV EXPORT


def export_grades_csv(request):
    # CSV-Download vorbereiten und Dateinamen für den Export festlegen
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="noten_export.csv"'

    # Verhindert Darstellungsfehler von Umlauten beim Öffnen in Excel
    response.write("\ufeff".encode("utf8"))

    writer = csv.writer(response, delimiter=";")

    # Kopfzeile
    writer.writerow(["Vorname", "Nachname", "Kurs", "Note"])

    # Alle Noten aus der Datenbank
    grades = Grade.objects.all().select_related("student", "course")
    for grade in grades:
        writer.writerow([grade.student.first_name, grade.student.last_name, grade.course.name, grade.score])

    return response


# CSV IMPORT


def import_grades_csv(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]

        # Prüfen, ob es eine CSV-Datei ist
        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Bitte lade eine gültige .csv-Datei hoch.")
            return redirect("dashboard")

        # Datei lesen
        decoded_file = csv_file.read().decode("utf-8")
        io_string = io.StringIO(decoded_file)
        reader = csv.reader(io_string, delimiter=";")

        next(reader)  # Kopfzeile nicht importieren (Vorname;Nachname;Kurs;Note)

        for row in reader:
            if len(row) >= 4:
                first_name, last_name, course_name, score_raw = row[0], row[1], row[2], row[3]

                # Student und Kurs in der Datenbank suchen oder erstellen
                student, _ = Student.objects.get_or_create(first_name=first_name, last_name=last_name)
                
                # max_score als Standardwert gesetzt, falls der Kurs neu ist
                course, _ = Course.objects.get_or_create(
                    name=course_name, 
                    defaults={'max_score': 100}
                )

                # Dezimalzahlen in ganze Zahlen umwandeln
                score = int(float(score_raw))

                # Note übernehmen
                Grade.objects.create(student=student, course=course, score=score)

        messages.success(request, "Noten wurden erfolgreich importiert!")
        return redirect("grades")

    return render(request, "import_csv.html")