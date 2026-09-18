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
    is_dozent_or_admin = request.user.is_superuser or request.user.groups.filter(name="Dozent").exists()

    student_count = Student.objects.count()
    course_count = Course.objects.count()
    grade_count = Grade.objects.count()
    at_risk_count = Grade.objects.filter(score__lt=50).count()

    # Daten Diagramm 1: Bestanden vs. Nicht Bestanden
    passed_count = Grade.objects.filter(score__gte=50).count()
    failed_count = Grade.objects.filter(score__lt=50).count()

    # Daten Diagramm 2: Verteilung nach Kursen
    course_data = Course.objects.annotate(grade_num=Count("grade")).filter(grade_num__gt=0)
    course_names = [c.name for c in course_data]
    course_counts = [c.grade_num for c in course_data]

    chart_pie = None
    chart_donut = None

    if Grade.objects.exists():
        # 1. Kreisdiagramm
        fig1, ax1 = plt.subplots(figsize=(5.5, 4.2))
        fig1.patch.set_facecolor("#ffffff")
        ax1.set_facecolor("#ffffff")

        pie_values = [passed_count or 1, failed_count or 0]
        wedges1, _ = ax1.pie(
            pie_values,
            colors=["#22c55e", "#ef4444"],
            startangle=90,
            wedgeprops={"edgecolor": "#ffffff", "linewidth": 1.5}
        )
        ax1.legend(
            wedges1,
            ["Bestanden", "Nicht bestanden"],
            loc="upper center",
            bbox_to_anchor=(0.5, 1.15),
            ncol=2,
            frameon=False,
            fontsize=9
        )
        plt.tight_layout()
        buf1 = io.BytesIO()
        plt.savefig(buf1, format="png", facecolor="#ffffff", edgecolor="none", dpi=110)
        buf1.seek(0)
        chart_pie = base64.b64encode(buf1.getvalue()).decode("utf-8")
        buf1.close()
        plt.close(fig1)

        # 2. Donut-Diagramm
        fig2, ax2 = plt.subplots(figsize=(5.5, 4.2))
        fig2.patch.set_facecolor("#ffffff")
        ax2.set_facecolor("#ffffff")

        palette = ["#f87171", "#34d399", "#fbbf24", "#38bdf8", "#60a5fa", "#c084fc", "#e879f9", "#111827"]
        donut_vals = course_counts if course_counts else [1]
        donut_lbls = course_names if course_names else ["Keine Daten"]

        wedges2, _ = ax2.pie(
            donut_vals,
            colors=palette[:len(donut_vals)],
            startangle=45,
            wedgeprops={"edgecolor": "#ffffff", "linewidth": 1.5, "width": 0.45}
        )
        ax2.legend(
            wedges2,
            donut_lbls,
            loc="upper center",
            bbox_to_anchor=(0.5, 1.15),
            ncol=3,
            frameon=False,
            fontsize=8
        )
        plt.tight_layout()
        buf2 = io.BytesIO()
        plt.savefig(buf2, format="png", facecolor="#ffffff", edgecolor="none", dpi=110)
        buf2.seek(0)
        chart_donut = base64.b64encode(buf2.getvalue()).decode("utf-8")
        buf2.close()
        plt.close(fig2)

    context = {
        "student_count": student_count,
        "course_count": course_count,
        "grade_count": grade_count,
        "at_risk_count": at_risk_count,
        "chart_pie": chart_pie,
        "chart_donut": chart_donut,
        "is_dozent_or_admin": is_dozent_or_admin,
    }
    return render(request, "dashboard.html", context)


# Neuen Studenten anlegen -für Dozenten,Super-Admins
@user_passes_test(is_dozent)
def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)

            # 1. Automatische ID generieren
            if not student.student_id:
                last_student = (
                    Student.objects.exclude(student_id__isnull=True).exclude(student_id="").order_by("-id").first()
                )
                if last_student and last_student.student_id and last_student.student_id.isdigit():
                    next_id = int(last_student.student_id) + 1
                else:
                    next_id = Student.objects.count() + 1
                student.student_id = f"{next_id:04d}"

            # 2. Prüfen/Erstellen  Django-Users
            if hasattr(student, "user") and not student.user:
                # generierte student_id als Benutzernamen
                username = student.email if student.email else student.student_id

                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1

                user = User.objects.create_user(username=username, email=student.email)
                student.user = user

            student.save()
            form.save_m2m()
            messages.success(request, "Student erfolgreich erstellt.")
            return redirect("students")
    else:
        form = StudentForm()
    return render(request, "student_form.html", {"form": form})


# Studenten bearbeiten -für Dozenten,Super-Admins
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


# Liste aller Studenten anzeigen mit Kursen und Noten
def students_view(request):
    is_dozent_or_admin = request.user.is_superuser or request.user.groups.filter(name="Dozent").exists()
    query = request.GET.get("q", "").strip()

    students = Student.objects.prefetch_related("grade_set__course")

    if query:
        students = students.filter(
            Q(student_id__icontains=query) |
            Q(last_name__icontains=query) |
            Q(first_name__icontains=query)
        )

    student_list = []
    for s in students:
        grades = list(s.grade_set.all())

        # Kurse und Notenanzahl pro Kurs ermitteln
        course_grade_counts = {}
        for g in grades:
            c_name = g.course.name
            course_grade_counts[c_name] = course_grade_counts.get(c_name, 0) + 1

        # Falls der Student in Kursen ohne vergebene Note eingeschrieben ist
        if hasattr(s, "enrolled_courses"):
            for ec in s.enrolled_courses.all():
                if ec.name not in course_grade_counts:
                    course_grade_counts[ec.name] = 0

        course_info = [
            {"course_name": c_name, "grade_count": count}
            for c_name, count in course_grade_counts.items()
        ]

        student_list.append({
            "obj": s,
            "courses": course_info,
            "total_grades": len(grades),
        })

    context = {
        "student_list": student_list,
        "query": query,
        "is_dozent_or_admin": is_dozent_or_admin,
    }
    return render(request, "students.html", context)

# Liste aller Kurse
def course_list(request):
    is_dozent_or_admin = request.user.is_superuser or request.user.groups.filter(name="Dozent").exists()
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "all")

    courses = Course.objects.prefetch_related("grade_set__student").all()

    if query:
        courses = courses.filter(name__icontains=query)

    course_data = []
    for c in courses:
        grades = list(c.grade_set.all())
        total_grades = len(grades)

        if status_filter == "with_grades" and total_grades == 0:
            continue
        if status_filter == "without_grades" and total_grades > 0:
            continue

        avg_score = round(sum(g.score for g in grades) / total_grades, 1) if total_grades > 0 else 0

        students_in_course = [
            {
                "name": f"{g.student.first_name} {g.student.last_name}",
                "student_id": g.student.student_id,
                "score": g.score,
                "passed": g.score >= 50
            }
            for g in grades
        ]

        course_data.append({
            "obj": c,
            "total_grades": total_grades,
            "avg_score": avg_score,
            "students": students_in_course
        })

    return render(request, "courses.html", {
        "course_data": course_data,
        "is_dozent_or_admin": is_dozent_or_admin,
        "query": query,
        "status_filter": status_filter
    })
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




# Kurs bearbeiten
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


# Liste aller Noten anzeigen (für Dozenten alle, für Studenten nur eigene)
def grades_view(request):
    is_dozent_or_admin = request.user.is_superuser or request.user.groups.filter(name="Dozent").exists()
    query = request.GET.get("q", "").strip()
    course_filter = request.GET.get("course", "")

    if is_dozent_or_admin:
        grades = Grade.objects.select_related("student", "course").all().order_by("-id")
        if query:
            grades = grades.filter(
                Q(student__first_name__icontains=query) |
                Q(student__last_name__icontains=query) |
                Q(student__student_id__icontains=query)
            )
        if course_filter:
            grades = grades.filter(course_id=course_filter)
    else:
        student = getattr(request.user, "student_profile", None)
        if not student:
            student = Student.objects.filter(student_id=request.user.username).first()
            if student and not student.user:
                student.user = request.user
                student.save(update_fields=["user"])

        if student:
            grades = Grade.objects.filter(student=student).select_related("course").order_by("course__name")
        else:
            grades = Grade.objects.none()

    courses = Course.objects.all()

    return render(request, "grades.html", {
        "grades": grades,
        "courses": courses,
        "query": query,
        "course_filter": course_filter,
        "is_dozent_or_admin": is_dozent_or_admin
    })


# Note erfassen
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
    is_dozent_or_admin = request.user.is_superuser or request.user.groups.filter(name="Dozent").exists()
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
    writer.writerow(["Student-ID", "Vorname", "Nachname", "E-Mail", "Kurs", "Note"])
    grades = Grade.objects.all().order_by("student__student_id")
    for g in grades:
        writer.writerow(
            [
                g.student.student_id,
                g.student.first_name,
                g.student.last_name,
                g.student.email or "",
                g.course.name,
                g.score,
            ]
        )

    return response


# Noten aus CSV-Datei importieren
@user_passes_test(is_dozent)
def import_grades_csv(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Bitte lade eine gültige .csv-Datei hoch.")
            return redirect("dashboard")

        # entfernt Excel-BOM-Zeichen
        decoded_file = csv_file.read().decode("utf-8-sig")
        io_string = io.StringIO(decoded_file)
        reader = csv.reader(io_string, delimiter=";")

        next(reader)

        for row in reader:
            if len(row) >= 6:
                student_id, first_name, last_name, email, course_name, score_raw = (
                    row[0].strip(),
                    row[1].strip(),
                    row[2].strip(),
                    row[3].strip(),
                    row[4].strip(),
                    row[5].strip(),
                )

                # Suche/Erstellung über die student_id
                student, created = Student.objects.get_or_create(
                    student_id=student_id, defaults={"first_name": first_name, "last_name": last_name, "email": email}
                )

                # Student da , dann aktualisieren
                updated = False
                if not created:
                    if first_name and student.first_name != first_name:
                        student.first_name = first_name
                        updated = True
                    if last_name and student.last_name != last_name:
                        student.last_name = last_name
                        updated = True
                    if email and not student.email:
                        student.email = email
                        updated = True
                    if updated:
                        student.save()

                course, _ = Course.objects.get_or_create(name=course_name, defaults={"max_score": 100})

                score = int(float(score_raw.replace(",", ".")))
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

    # 1. Studenten über das Profil oder per Username (student_id) zu finden
    student = getattr(request.user, "student_profile", None)
    if not student:
        student = Student.objects.filter(student_id=request.user.username).first()
        # Falls gefunden, verknüpfen
        if student and not student.user:
            student.user = request.user
            student.save(update_fields=["user"])

    if student:
        if course in student.enrolled_courses.all():
            messages.warning(request, f"Du bist bereits für den Kurs '{course.name}' angemeldet.")
        else:
            course.students.add(student)
            messages.success(request, f"Du hast dich erfolgreich für '{course.name}' angemeldet.")
    else:
        messages.error(request, "Nur vorhandene Studenten können sich zu Kursen anmelden.")

    return redirect("courses")
