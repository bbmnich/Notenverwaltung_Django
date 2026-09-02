from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver


# Studenten
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="student_profile")
    student_id = models.CharField(max_length=20, unique=True, verbose_name="Studenten-ID", blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="student_profile")

    def save(self, *args, **kwargs):
        # Wenn der Student noch keinen verknüpften User hat, erstellen wir einen
        if not self.user and self.student_id:
            user, created = User.objects.get_or_create(
                username=self.student_id,
                defaults={"first_name": self.first_name, "last_name": self.last_name, "email": self.email or ""},
            )
            if created:
                user.set_password("student")  # Standardpasswort
                user.save()
                # Der Gruppe 'Student' zuweisen
                student_group, _ = Group.objects.get_or_create(name="Student")
                user.groups.add(student_group)

            self.user = user

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"


# Kurs
class Course(models.Model):
    name = models.CharField(max_length=100)
    max_score = models.IntegerField()

    # Kurseinschreibung für Studenten
    students = models.ManyToManyField(Student, blank=True, related_name="enrolled_courses")

    def __str__(self):
        return self.name + " (Max: " + str(self.max_score) + ")"


# Noten
class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.course.name}: {self.score} Punkte"


# --- Automatisches Erstellen des Login-student---
@receiver(post_save, sender=Student)
def create_user_for_student(sender, instance, created, **kwargs):
    if created and not instance.user:
        # Automatisch generierte student_id als Benutzernamen
        username = instance.student_id

        user, user_created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": instance.email,
                "first_name": instance.first_name,
                "last_name": instance.last_name,
            },
        )

        if user_created:
            # Standard-Passwort setzen
            user.set_password("student")
            user.save()

            # Automatisch zur Gruppe 'Student' hinzufügen
            student_group, _ = Group.objects.get_or_create(name="Student")
            user.groups.add(student_group)

        # Verknüpfung im Studenten-Modell
        instance.user = user
        instance.save(update_fields=["user"])
