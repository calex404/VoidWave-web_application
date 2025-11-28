# core/forms.py (KOMPLETNÝ A OPRAVENÝ KÓD)

from django import forms
from django.contrib.auth.forms import UserCreationForm 
from .models import Profil, Rola, Udalost, Tim, Hodnotenie
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

        default_role = Rola.objects.filter(nazov_role='Hráč').first() 

        profil = Profil.objects.create(
            user=user, 
            nickname=self.cleaned_data.get('nickname'), 
            bio=self.cleaned_data.get('bio'),
            rola=default_role 
        )
        profil.user = user
        profil.save()
        
        return user

# --- 2. FORMULÁR PRE UDALOSTI ---

from django import forms
from .models import Udalost # ... a ostatné importy, ak nejaké máš

# core/forms.py (Opravený UdalostForm)

# ... (ostatné formuláre) ...

# --- 2. FORMULÁR PRE UDALOSTI ---
class UdalostForm(forms.ModelForm):
    class Meta:
        model = Udalost
        # 💥 FIX: Odstránené neexistujúce pole 'max_ucastnikov' 💥
        fields = ['nazov', 'datum_konania', 'popis', 'hra', 'typ'] 
        widgets = {
            # NOVÝ WIDGET PRE DÁTUM A ČAS
            'datum_konania': forms.DateTimeInput(attrs={'type': 'datetime-local'}), 
        }
# --- 3. FORMULÁR PRE TÍMY ---
class TimForm(forms.ModelForm):
    class Meta:
        model = Tim
        fields = ['nazov', 'bio']
        labels = {
            'nazov': 'Názov tímu',
            'bio': 'Popis tímu (napr. hráme len CS:GO)'
        }

# --- 4. 💥 CHÝBAJÚCI FORMULÁR PRE EDITÁCIU PROFILU 💥 ---
class ProfilEditForm(forms.ModelForm):
    class Meta:
        model = Profil
        fields = ['nickname', 'bio']
        labels = {
            'nickname': 'Prezývka (viditeľná)',
            'bio': 'O mne'
        }

# core/forms.py (Iba sekcia pre Hodnotenie)

# Uisti sa, že máš hore importovaný aj model Hodnotenie!
# from .models import Profil, Rola, Udalost, Tim, Hodnotenie # <--- MUSÍ BYŤ PRÍTOMNÝ HORE

HODNOTENIE_CHOICES = [(i, str(i)) for i in range(1, 11)]

class HodnotenieForm(forms.ModelForm):
    hodnotenie = forms.ChoiceField(choices=HODNOTENIE_CHOICES, label="Tvoje hodnotenie (1-10)")

    class Meta:
        model = Hodnotenie
        fields = ['hodnotenie']