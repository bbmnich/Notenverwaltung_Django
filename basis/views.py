from django.shortcuts import render
from .models import Student, Course, Grade

def startseite(request):
    meldung_student = ""
    meldung_kurs = ""

    if request.method == "POST":
        
        #  TEILNEHMER HINZUFÜGEN 
        # Prüfen, ob ein neuer Teilnehmer eingegeben wurde
        if "eingabe_vorname" in request.POST:
            roher_vorname = request.POST.get("eingabe_vorname")
            roher_nachname = request.POST.get("eingabe_nachname")
            
            vorname_sauber = roher_vorname.strip().capitalize()
            nachname_sauber = roher_nachname.strip().capitalize()
            neuer_name = vorname_sauber + " " + nachname_sauber
            
            # INFO bei leeren Feldern
            if vorname_sauber == "" or nachname_sauber == "":
                meldung_student = "Info: Bitte Vorname und Nachname ausfüllen."
            else:
                # Prüfen, ob der Name schon in der Datenbank steht
                student_existiert = Student.objects.filter(name=neuer_name).exists()
                if student_existiert:
                    meldung_student = "Info: Der Teilnehmer " + neuer_name + " existiert bereits."
                else:
                    # Neuen Teilnehmer speichern
                    neuer_student = Student(name=neuer_name)
                    neuer_student.save()
                    meldung_student = "Erfolg: Teilnehmer " + neuer_name + " wurde hinzugefügt!"

        #  TEILNEHMER LÖSCHEN
        # Prüfen, ob ein Teilnehmer zum Löschen ausgewählt wurde
        elif "student_loeschen_id" in request.POST:
            s_id = request.POST.get("student_loeschen_id")
            
            # INFO wenn nichts ausgewählt wurde
            if s_id == "":
                meldung_student = "Info: Bitte wählen Sie einen Teilnehmer zum Löschen aus."
            else:
                # Teilnehmer in der Datenbank suchen und entfernen
                zu_loschender_student = Student.objects.get(id=s_id)
                zu_loschender_student.delete()
                meldung_student = "Info: Teilnehmer mit ID " + str(s_id) + " erfolgreich gelöscht!"

        # KURS HINZUFÜGEN
        # Prüfen, ob ein neuer Kurs eingegeben wurde
        elif "eingabe_kurs" in request.POST:
            roher_kurs = request.POST.get("eingabe_kurs")
            neuer_kurs = roher_kurs.strip().capitalize()
            
            # INFO bei leerem Feld
            if neuer_kurs == "":
                meldung_kurs = "Info: Bitte einen Kursnamen eingeben."
            else:
                # Prüfen, ob der Kurs schon in der Datenbank steht
                kurs_existiert = Course.objects.filter(name=neuer_kurs).exists()
                if kurs_existiert:
                    meldung_kurs = "Info: Der Kurs " + neuer_kurs + " existiert bereits."
                else:
                    # Neuen Kurs speichern
                    neuer_kurs_db = Course(name=neuer_kurs, max_score=100)
                    neuer_kurs_db.save()
                    meldung_kurs = "Erfolg: Kurs " + neuer_kurs + " wurde angelegt!"

        # --- KURS LÖSCHEN ---
        # Prüfen, ob ein Kurs zum Löschen ausgewählt wurde
        elif "kurs_loeschen_id" in request.POST:
            c_id = request.POST.get("kurs_loeschen_id")
            
            # INFO wenn nichts ausgewählt wurde
            if c_id == "":
                meldung_kurs = "Info: Bitte wählen Sie einen Kurs zum Löschen aus."
            else:
                # Kurs in der Datenbank suchen und entfernen
                zu_loschender_kurs = Course.objects.get(id=c_id)
                zu_loschender_kurs.delete()
                meldung_kurs = "Info: Kurs mit ID " + str(c_id) + " erfolgreich gelöscht!"

    # Alle aktuellen Daten für die Anzeige laden
    alle_studenten = Student.objects.all()
    alle_kurse = Course.objects.all()

    # Daten und Meldungen an die Seite übergeben
    return render(request, "startseite.html", {
        "alle_studenten": alle_studenten, 
        "alle_kurse": alle_kurse,
        "meldung_student": meldung_student,
        "meldung_kurs": meldung_kurs
    })

