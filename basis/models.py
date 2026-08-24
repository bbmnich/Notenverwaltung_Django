from django.db import models
#Studenten
class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(default="")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


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
        return (
            self.student.name
            + " - "
            + self.course.name
            + ": "
            + str(self.score)
            + " Punkte"
        )
