from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.db.models import Q 
from .models import (
    Profil, Rola, Udalost, Tim, Hodnotenie
)

HODNOTENIE_CHOICES = [(i, str(i)) for i in range(1, 11)]

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """
    Formulár pre registráciu, ktorý rozširuje štandardnú tvorbu Usera 
    o povinné polia 'nickname' a 'bio' a zabezpečuje vytvorenie modelu Profil.
    """
    nickname = forms.CharField(max_length=255, required=True, help_text="Viditeľná prezývka na platforme.")
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, help_text="Krátky popis seba samého.")
    email = forms.EmailField(required=False, help_text="Voliteľné: Adresa pre notifikácie.")

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email', 'nickname', 'bio')

    def save(self, commit=True):
        """Uloží Usera a automaticky mu vytvorí model Profil."""
        user = super().save(commit=True)

        default_role = Rola.objects.filter(nazov_role='Hráč').first()
        
        profil = Profil.objects.create(
            user=user, 
            nickname=self.cleaned_data.get('nickname'), 
            bio=self.cleaned_data.get('bio'),
            rola=default_role 
        )

        return user


class ProfilEditForm(forms.ModelForm):
    """Formulár pre editáciu existujúceho modelu Profil (zobrazuje sa na Dashboarde)."""
    class Meta:
        model = Profil
        fields = ['nickname', 'bio']
        labels = {
            'nickname': 'Prezývka (viditeľná)',
            'bio': 'O mne'
        }


class UdalostForm(forms.ModelForm):
    """Formulár na vytváranie novej udalosti."""
    class Meta:
        model = Udalost
        fields = ['nazov', 'datum_konania', 'popis', 'hra', 'typ']
        widgets = {
            'datum_konania': forms.DateTimeInput(attrs={'type': 'datetime-local'}), 
        }


class HodnotenieForm(forms.ModelForm):
    """Formulár na hodnotenie udalosti (zobrazuje sa v archíve)."""
    hodnotenie = forms.ChoiceField(choices=HODNOTENIE_CHOICES, label="Tvoje hodnotenie (1-10)")

    class Meta:
        model = Hodnotenie
        fields = ['hodnotenie'] 


class TimForm(forms.ModelForm):
    """Formulár na zakladanie nového tímu."""
    class Meta:
        model = Tim
        fields = ['nazov', 'bio']
        labels = {
            'nazov': 'Názov tímu',
            'bio': 'Popis tímu (napr. hráme len CS:GO)'
        }