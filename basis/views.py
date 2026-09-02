import base64
import csv
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User, Group
from django.db.models import Avg, Max, Min, Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CourseForm, GradeForm, StudentForm
from .models import Student, Course, Grade


# --- ROLLEN ---
def is_super_admin(user):
    return user.is_superuser


def is_dozent(user):
    return user.is_superuser or user.groups.filter(name="Dozent").exists()


def is_student(user):
    return user.groups.filter(name="Student").exists()


# Dashboard-Ansicht mit Kennzahlen
def dashboard_view(request):
    is_dozent_or_admin = request.user.is_superuser or request.user.groups.filter(name='Dozent').exists()
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
        "is_dozent_or_admin": is_dozent_or_admin,
    }
    return render(request, "dashboard.html", context)


# Neuen Studenten anlegen -für Dozenten ,Super-Admins
@user_passes_test(is_dozent)
def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("students")
    else:
        form = StudentForm()
    return render(request, "student_form.html", {"form": form})


# Studenten bearbeiten -für Dozenten ,Super-Admins
@user_passes_test(is_dozent)
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


# Studenten löschen -für Dozenten, Super-Admins
@user_passes_test(is_dozent)
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.delete()
        return redirect("students")
    return render(request, "student_delete.html", {"student": student})


# Liste aller Studenten anzeigen (Suche nach ID oder Nachname)
def students_view(request):
    is_dozent_or_admin = request.user.is_superuser or request.user.groups.filter(name='Dozent').exists()
    query = request.GET.get("q", "").strip()

    if query:
        students = Student.objects.filter(Q(student_id__icontains=query) | Q(last_name__icontains=query))
    else:
        students = Student.objects.all()

    context = {
        "students": students,
        "query": query,
        "is_dozent_or_admin": is_dozent_or_admin,
    }
    return render(request, "students.html", context)


# Liste aller Kurse anzeigen
def course_list(request):
    is_dozent_or_admin = request.user.is_superuser or request.user.groups.filter(name='Dozent').exists()
    courses = Course.objects.all()
    return render(request, "courses.html", {"courses": courses, "is_dozent_or_admin": is_dozent_or_admin})


# Neuen Kurs erstellen
@user_passes_test(is_dozent)
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
@user_passes_test(is_dozent)
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
@user_passes_test(is_dozent)
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        course.delete()
        return redirect("courses")
    return render(request, "course_delete.html", {"course": course})


# Liste aller Noten anzeigen (für Dozenten alle, für Studenten nur die eigenen)
def grades_view(request):
    is_dozent_or_admin = request.user.is_superuser or request.user.groups.filter(name='Dozent').exists()
    
    if is_dozent_or_admin:
        grades = Grade.objects.all().order_by("student__last_name")
    elif hasattr(request.user, "student_profile") and request.user.student_profile:
        grades = Grade.objects.filter(student=request.user.student_profile).order_by("course__name")
    else:
        grades = Grade.objects.none()
        
    return render(request, "grades.html", {"grades": grades, "is_dozent_or_admin": is_dozent_or_admin})

# Einzelne Note erfassen
@user_passes_test(is_dozent)
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
@user_passes_test(is_dozent)
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
@user_passes_test(is_dozent)
def grade_delete(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    if request.method == "POST":
        grade.delete()
        return redirect("grades")
    return render(request, "grade_delete.html", {"grade": grade})


# Auswertungen und Statistiken für Studenten und Kurse
def reports_view(request):
    is_dozent_or_admin = request.user.is_superuser or request.user.groups.filter(name='Dozent').exists()
    total_grades = Grade.objects.count()
    overall_avg = Grade.objects.aggregate(Avg("score"))["score__avg"] or 0
    highest_grade = Grade.objects.aggregate(Max("score"))["score__max"]
    lowest_grade = Grade.objects.aggregate(Min("score"))["score__min"]

    passed_count = Grade.objects.filter(score__gte=50).count()
    failed_count = Grade.objects.filter(score__lt=50).count()
    pass_rate = round((passed_count / total_grades * 100), 1) if total_grades > 0 else 0

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

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", facecolor=fig.get_facecolor(), edgecolor="none")
    buffer.seek(0)
    pass_fail_chart = base64.b64encode(buffer.read()).decode("utf-8")
    buffer.close()
    plt.close(fig)

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
        "is_dozent_or_admin": is_dozent_or_admin,
    }
    return render(request, "reports.html", context)


# Noten als CSV-Datei exportieren
def export_grades_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="noten_export.csv"'
    response.write("\ufeff".encode("utf8"))

    writer = csv.writer(response, delimiter=";")
    writer.writerow(["Vorname", "Nachname", "Kurs", "Note"])

    grades = Grade.objects.all().select_related("student", "course")
    for grade in grades:
        writer.writerow([grade.student.first_name, grade.student.last_name, grade.course.name, grade.score])

    return response


# Noten aus CSV-Datei importieren
@user_passes_test(is_dozent)
def import_grades_csv(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Bitte lade eine gültige .csv-Datei hoch.")
            return redirect("dashboard")

        decoded_file = csv_file.read().decode("utf-8")
        io_string = io.StringIO(decoded_file)
        reader = csv.reader(io_string, delimiter=";")

        next(reader)

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
@user_passes_test(is_dozent)
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
@user_passes_test(is_super_admin)
def admin_bereich_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        group_name = request.POST.get("group_name")

        if username and password:
            if User.objects.filter(username=username).exists():
                messages.error(request, f"Der Benutzername '{username}' existiert bereits.")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)

                if group_name:
                    try:
                        group = Group.objects.get(name=group_name)
                        user.groups.add(group)
                    except Group.DoesNotExist:
                        pass

                messages.success(
                    request, f"Benutzer '{username}' wurde erfolgreich als {group_name or 'Standard'} erstellt!"
                )
                return redirect("admin_bereich")

    users = User.objects.prefetch_related("groups", "student_profile").all()
    groups = Group.objects.all()

    context = {
        "users": users,
        "groups": groups,
    }
    return render(request, "admin_bereich.html", context)


# Kurs-Anmeldung für Studenten
@login_required
def course_enroll(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if hasattr(request.user, "student_profile") and request.user.student_profile:
        student = request.user.student_profile
        if course in student.enrolled_courses.all():
            messages.warning(request, f"Du bist bereits für den Kurs '{course.name}' angemeldet.")
        else:
            course.students.add(student)
            messages.success(request, f"Du hast dich erfolgreich für '{course.name}' angemeldet.")
    else:
        messages.error(request, "Nur vorhandene Studenten können sich zu Kursen anmelden.")

    return redirect("courses")