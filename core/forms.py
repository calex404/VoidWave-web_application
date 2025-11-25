# core/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm 
# 💥 DÔLEŽITÉ: Musíme importovať aj model Tim
from .models import Profil, Rola, Udalost, Tim
from django.contrib.auth import get_user_model 

User = get_user_model()

# --- 1. REGISTRAČNÝ FORMULÁR ---
class CustomUserCreationForm(UserCreationForm):
    
    nickname = forms.CharField(max_length=255, required=True, help_text="Viditeľná prezývka na platforme.")
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, help_text="Krátky popis seba samého.")
    email = forms.EmailField(required=False, help_text="Voliteľné: Adresa pre notifikácie.")

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email', 'nickname', 'bio')

    def save(self, commit=True):
        user = super().save(commit=True)
        user.email = self.cleaned_data['email']
        user.save()

        # Nájdenie roly
        default_role = Rola.objects.filter(nazov_role='Hráč').first() 

        # Vytvorenie profilu
        profil = Profil.objects.create(
            nickname=self.cleaned_data.get('nickname'), 
            bio=self.cleaned_data.get('bio'),
            rola=default_role 
        )
        # Priradenie Usera k Profilu
        profil.user = user
        profil.save()
        
        return user

# --- 2. FORMULÁR PRE UDALOSTI ---
class UdalostForm(forms.ModelForm):
    class Meta:
        model = Udalost
        fields = ['nazov', 'typ', 'hra', 'datum_konania', 'popis']
        widgets = {
            'datum_konania': forms.DateInput(attrs={'type': 'date'}),
        }

# --- 3. 💥 CHÝBAJÚCI FORMULÁR PRE TÍMY 💥 ---
class TimForm(forms.ModelForm):
    class Meta:
        model = Tim
        fields = ['nazov', 'bio']
        labels = {
            'nazov': 'Názov tímu',
            'bio': 'Popis tímu (napr. hráme len CS:GO)'
        }