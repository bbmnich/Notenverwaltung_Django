from django.shortcuts import render
from .models import Student

def startseite(request):
    # Leerer Standardwert, falls kein neuer Student gespeichert wird.
    meldung = ""

    if request.method == "POST":
        # Hat der Nutzer Daten gesendet? 2. Rohen Text aus dem Feld holen. 3. Text mit .strip() bereinigen.
        roher_name = request.POST.get("eingabe_name")
        neuer_name = roher_name.strip()
        
        # Leerzeichen Prüfung
        if neuer_name == "":
            meldung = "Fehler: Der Name darf nicht leer sein."
        else:
            # Duplikate verhindern
            student_existiert = Student.objects.filter(name=neuer_name).exists()
            
            if student_existiert:
                meldung = "Fehler: Der Student " + neuer_name + " existiert bereits!"
            else:
                # Nur wenn alle Prüfungen Ok wird gespeichert
                neuer_student = Student(name=neuer_name)
                neuer_student.save()
                meldung = "Erfolg: " + neuer_name + " wurde angelegt!"

    # aktualisierte Liste aus der Datenbank holen
    alle_studenten = Student.objects.all()

    # Studenten UND die neue Meldung anzeigen
    return render(request, "startseite.html", {"alle_studenten": alle_studenten, "meldung": meldung})