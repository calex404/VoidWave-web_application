# core/forms.py (NÁVRAT K BEZPEČNÉMU HĽADANIU PODĽA MENA)

from django import forms
from django.contrib.auth.forms import UserCreationForm 
from .models import Profil, Rola
from django.contrib.auth import get_user_model 

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    
    nickname = forms.CharField(max_length=255, required=True, help_text="Viditeľná prezývka na platforme.")
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, help_text="Krátky popis seba samého.")
    email = forms.EmailField(required=False, help_text="Voliteľné: Adresa pre notifikácie.")


    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email', 'nickname', 'bio')


    def save(self, commit=True):
        # 1. Uloží používateľa do Djangovského User modelu:
        user = super().save(commit=True)
        user.email = self.cleaned_data['email']
        user.save()

        # 2. 💥 BEZPEČNÉ HĽADANIE ROLY PODĽA MENA 💥
        # Hľadá rolu "Hráč". AK MÁŠ INÉ MENO (napr. 'hráč'), ZMEŇ HO TU!
        default_role = Rola.objects.filter(nazov_role='Hráč').first() 

        # 3. PRIRADENIE ROLY a PREPOJENIE
        profil = Profil.objects.create(
            user=user, 
            nickname=self.cleaned_data.get('nickname'), 
            bio=self.cleaned_data.get('bio'),
            rola=default_role 
        )
        
        return user