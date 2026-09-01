from django.db import models


# Studenten
class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True, verbose_name="Studenten-ID", blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.student_id:
            # Alle vorhandenen numerischen IDs durchgehen
            existing_ids = Student.objects.exclude(student_id__isnull=True).exclude(student_id__exact="")
            numeric_ids = []
            for s in existing_ids:
                if s.student_id and s.student_id.isdigit():
                    numeric_ids.append(int(s.student_id))

            if numeric_ids:
                next_num = max(numeric_ids) + 1
            else:
                next_num = 1

            # Falls die ID doch existiert, solange +1 rechnen bis sie frei ist
            while Student.objects.filter(student_id=f"{next_num:04d}").exists():
                next_num += 1

            self.student_id = f"{next_num:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"

        # Sicherheitsschleife: Falls die ID doch existiert, solange +1 rechnen bis sie frei ist
        while Student.objects.filter(student_id=f"{next_num:04d}").exists():
            next_num += 1

        self.student_id = f"{next_num:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"


# Kurs
class Course(models.Model):
    name = models.CharField(max_length=100)
    max_score = models.IntegerField()

    def __str__(self):
        return self.name + " (Max: " + str(self.max_score) + ")"


# Noten
class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return self.student.name + " - " + self.course.name + ": " + str(self.score) + " Punkte"
