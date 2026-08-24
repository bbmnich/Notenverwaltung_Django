import re
from django import forms
from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["first_name", "last_name", "email"]

        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Vorname (z. B. Anna-Maria)"}),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nachname (z. B. Müller-Schmidt)"}
            ),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "E-Mail-Adresse"}),
        }

    # Überprüfung für den Vornamen (erlaubt Buchstaben, Umlaute, Leerzeichen und Bindestriche)
    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        # Prüfung  auf Buchstaben (Umlaute), Leerzeichen und Bindestriche
        if not re.match(r"^[A-Za-zÄÖÜäöüß\s\-]+$", first_name):
            raise forms.ValidationError(
                "Der Vorname enthält ungültige Zeichen. Bindestriche für Doppelnamen sind erlaubt."
            )
        return first_name

    # Überprüfung für den Nachnamen (erlaubt Buchstaben, Umlaute, Leerzeichen und Bindestriche)
    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if not re.match(r"^[A-Za-zÄÖÜäöüß\s\-]+$", last_name):
            raise forms.ValidationError(
                "Der Nachname enthält ungültige Zeichen. Bindestriche für Doppelnamen sind erlaubt."
            )
        return last_name
