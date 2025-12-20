from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.db.models import Q 
from .models import (
    Profil, Rola, Udalost, Tim, Hodnotenie
)


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):

    nickname = forms.CharField(max_length=255, required=True, help_text="Viditeľná prezývka na platforme.")
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, help_text="Krátky popis seba samého.")
    email = forms.EmailField(required=False, help_text="Voliteľné: Adresa pre notifikácie.")

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email', 'nickname', 'bio')

    def save(self, commit=True):

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

    class Meta:
        model = Profil
        fields = ['nickname', 'bio']
        labels = {
            'nickname': 'Prezývka',
            'bio': 'O mne'
        }


class UdalostForm(forms.ModelForm):

    class Meta:
        model = Udalost
        fields = ['nazov', 'datum_konania', 'popis', 'hra', 'typ']
        widgets = {
            'datum_konania': forms.DateTimeInput(attrs={'type': 'datetime-local'}), 
        }


class HodnotenieForm(forms.ModelForm):

    HODNOTENIE_CHOICES = [(i, str(i)) for i in range(1, 11)]
    hodnotenie = forms.ChoiceField(choices=HODNOTENIE_CHOICES, label="Tvoje hodnotenie (1-10)")

    class Meta:
        model = Hodnotenie
        fields = ['hodnotenie'] 


class TimForm(forms.ModelForm):

    class Meta:
        model = Tim
        fields = ['nazov', 'bio']
        labels = {
            'nazov': 'Názov tímu',
            'bio': 'Popis tímu'
        }