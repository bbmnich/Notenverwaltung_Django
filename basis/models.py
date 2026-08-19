from django.db import models

# Student
class Student(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    email = models.EmailField(default="")

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