from django.shortcuts import render, redirect, get_object_or_404
from .forms import CourseForm, GradeForm, StudentForm
from .models import Student, Course, Grade
import csv
from django.http import HttpResponse
import io
from django.contrib import messages
import matplotlib
from django.db.models import Avg, Max, Min, Count, Q

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import io
import base64


# Dashboard-Ansicht mit Kennzahlen und Matplotlib-Notenverteilung
def dashboard_view(request):
    student_count = Student.objects.count()
    course_count = Course.objects.count()
    grade_count = Grade.objects.count()

    raw_distribution = Grade.objects.values("score").annotate(count=Count("id")).order_by("score")

    scores = [item["score"] for item in raw_distribution]
    counts = [item["count"] for item in raw_distribution]

    chart_image = None
    if scores and counts:
        fig, ax = plt.subplots(figsize=(10, 4.5))
        fig.patch.set_facecolor("#16161e")
        ax.set_facecolor("#16161e")

        # Noten als Text konvertieren, um Lücken im Diagramm zu vermeiden
        score_labels = [str(s) for s in scores]

        ax.bar(score_labels, counts, color="#8b5cf6", width=0.6, alpha=0.9)

        ax.set_xlabel("SCORE", color="#8b8b9e", fontsize=12, labelpad=10)
        ax.set_ylabel("ANZAHL", color="#8b8b9e", fontsize=12, labelpad=10)
        ax.tick_params(colors="#ffffff", labelsize=10)

        plt.xticks(rotation=0, color="#ffffff", fontsize=9)
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        ax.spines["bottom"].set_color("#2a2a35")
        ax.spines["left"].set_color("#2a2a35")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax.yaxis.grid(True, linestyle="--", alpha=0.2, color="#ffffff")
        ax.set_axisbelow(True)

        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", facecolor=fig.get_facecolor(), edgecolor="none", dpi=100)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close(fig)

        chart_image = base64.b64encode(image_png).decode("utf-8")

    context = {
        "student_count": student_count,
        "course_count": course_count,
        "grade_count": grade_count,
        "chart_image": chart_image,
    }
    return render(request, "dashboard.html", context)


# Neuen Studenten anlegen
def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("students")
    else:
        form = StudentForm()
    return render(request, "student_form.html", {"form": form})


# Studenten bearbeiten
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


# Studenten löschen
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.delete()
        return redirect("students")
    return render(request, "student_delete.html", {"student": student})


# Liste aller Studenten anzeigen (absteigend nach ID)
def students_view(request):
    # Suchbegriff auslesen und Leerzeichen entfernen
    query = request.GET.get('q', '').strip()
    
    if query:
        # Suche nach student_id oder Nachname
        students = Student.objects.filter(
            Q(student_id__icontains=query) | Q(last_name__icontains=query)
        )
    else:
        # Alle Studenten anzeigen
        students = Student.objects.all()

    context = {
        "students": students,
        "query": query,
    }
    return render(request, "students.html", context)


# Liste aller Kurse anzeigen
def course_list(request):
    courses = Course.objects.all()
    return render(request, "courses.html", {"courses": courses})


# Neuen Kurs erstellen
def course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("courses")
    else:
        form = CourseForm()
    return render(request, "course_form.html", {"form": form})


# Bestehenden Kurs bearbeiten
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


# Kurs löschen
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        course.delete()
        return redirect("courses")
    return render(request, "course_delete.html", {"course": course})


# Liste aller Noten sortiert nach Nachname anzeigen
def grades_view(request):
    grades = Grade.objects.all().order_by("student__last_name")
    return render(request, "grades.html", {"grades": grades})


# Einzelne Note erfassen
def grade_create(request):
    if request.method == "POST":
        form = GradeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("grades")
    else:
        form = GradeForm()
    return render(request, "grade_form.html", {"form": form})


# Note bearbeiten
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


# Note löschen
def grade_delete(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    if request.method == "POST":
        grade.delete()
        return redirect("grades")
    return render(request, "grade_delete.html", {"grade": grade})

    # Zeigt die Admin-Oberfläche an
    return render(request, "admin_bereich.html")


# Auswertungen und Statistiken für Studenten und Kurse
def reports_view(request):
    total_grades = Grade.objects.count()
    overall_avg = Grade.objects.aggregate(Avg("score"))["score__avg"] or 0
    highest_grade = Grade.objects.aggregate(Max("score"))["score__max"]
    lowest_grade = Grade.objects.aggregate(Min("score"))["score__min"]
    # Bestanden und Nicht bestanden ermitteln (Grenze: 50 Pkt.)
    passed_count = Grade.objects.filter(score__gte=50).count()
    failed_count = Grade.objects.filter(score__lt=50).count()
    pass_rate = round((passed_count / total_grades * 100), 1) if total_grades > 0 else 0

    # Diagramm Bestanden / Nicht bestanden
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor("#16161e")
    ax.set_facecolor("#16161e")

    categories = ["Bestanden", "Nicht bestanden"]
    counts = [passed_count, failed_count]
    colors = ["#09ef24", "#f20bee"]

    bars = ax.bar(categories, counts, color=colors, width=0.5)

    ax.spines["bottom"].set_color("#2a2a35")
    ax.spines["top"].set_color("#16161e")
    ax.spines["left"].set_color("#2a2a35")
    ax.spines["right"].set_color("#16161e")
    ax.tick_params(colors="#8b8b9e", labelsize=10)
    ax.title.set_color("#ffffff")

    ax.set_title("Gesamtübersicht: Bestanden vs. Nicht bestanden", fontsize=12, pad=15, color="#ffffff")
    ax.set_ylabel("Anzahl der Studenten", fontsize=10, color="#ffffff")
    # Werte mit Balken darstellen
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            color="#ffffff",
            fontsize=10,
        )
        plt.tight_layout()
    # Diagramm im Speicher und in Base64 konvertieren
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", facecolor=fig.get_facecolor(), edgecolor="none")
    buffer.seek(0)
    pass_fail_chart = base64.b64encode(buffer.read()).decode("utf-8")
    buffer.close()
    plt.close(fig)
    # Detaildaten für Studenten und Kurse
    students = Student.objects.annotate(
        passed_count=Count("grade", filter=Q(grade__score__gte=50)),
        failed_count=Count("grade", filter=Q(grade__score__lt=50)),
        grade_count=Count("grade"),
    )

    courses = Course.objects.annotate(
        avg_score=Avg("grade__score"),
        grade_count=Count("grade"),
        highest_score=Max("grade__score"),
        lowest_score=Min("grade__score"),
    )
    # Wertepakete an das HTML-Template senden
    context = {
        "total_grades": total_grades,
        "overall_avg": round(overall_avg, 2),
        "highest_grade": highest_grade,
        "lowest_grade": lowest_grade,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "pass_rate": pass_rate,
        "student_averages": students,
        "course_averages": courses,
        "pass_fail_chart": pass_fail_chart,
    }
    return render(request, "reports.html", context)


# Noten als CSV-Datei exportieren
def export_grades_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="noten_export.csv"'
    response.write("\ufeff".encode("utf8"))  # UTF-8 BOM für Excel-Kompatibilität

    writer = csv.writer(response, delimiter=";")
    writer.writerow(["Vorname", "Nachname", "Kurs", "Note"])

    grades = Grade.objects.all().select_related("student", "course")
    for grade in grades:
        writer.writerow([grade.student.first_name, grade.student.last_name, grade.course.name, grade.score])

    return response


# Noten aus CSV-Datei importieren
def import_grades_csv(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Bitte lade eine gültige .csv-Datei hoch.")
            return redirect("dashboard")

        decoded_file = csv_file.read().decode("utf-8")
        io_string = io.StringIO(decoded_file)
        reader = csv.reader(io_string, delimiter=";")

        next(reader)  # Kopfzeile überspringen

        for row in reader:
            if len(row) >= 5:
                first_name, last_name, email, course_name, score_raw = row[0], row[1], row[2], row[3], row[4]

                student, created = Student.objects.get_or_create(
                    first_name=first_name, last_name=last_name, defaults={"email": email}
                )

                if not created and email and not student.email:
                    student.email = email
                    student.save()

                course, _ = Course.objects.get_or_create(name=course_name, defaults={"max_score": 100})

                score = int(float(score_raw))
                Grade.objects.create(student=student, course=course, score=score)

        messages.success(request, "Alle Daten wurden erfolgreich importiert!")
        return redirect("grades")

    return render(request, "import_csv.html")


# Mehrere ausgewählte Studenten löschen
def student_bulk_delete(request):
    if request.method == "POST":
        selected_ids = request.POST.getlist("selected_students")
        if selected_ids:
            Student.objects.filter(id__in=selected_ids).delete()
            messages.success(request, f"{len(selected_ids)} Studenten wurden erfolgreich gelöscht.")
        else:
            messages.warning(request, "Es wurden keine Studenten ausgewählt.")
    return redirect("students")


# Admin-Bereich
def admin_bereich_view(request):
    return render(request, "admin_bereich.html")
