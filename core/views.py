# core/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Profil, Hra, Udalost
from .forms import CustomUserCreationForm 
from datetime import datetime
from django.contrib.auth.forms import AuthenticationForm # 💥 MUSÍ BYŤ IMPORT - Pre login form


def profil_list_view(request):
    
    vsetky_profily = Profil.objects.all()
    context = {
        'profily': vsetky_profily,
        'datum_a_cas': datetime.now()
    }
    
    # 💥 KRITICKÉ: Ak nie je používateľ prihlásený, pošleme prázdny prihlasovací formulár
    if not request.user.is_authenticated:
        # Vytvoríme formulár pre prihlásenie a pošleme ho do HTML ako 'form'
        context['form'] = AuthenticationForm() 
        
    return render(request, 'core/profil_list.html', context)


def hra_list_view(request):
    """Zobrazí zoznam všetkých dostupných hier."""
    
    vsetky_hry = Hra.objects.all()
    
    context = {
        'hry': vsetky_hry,
        'nadpis': 'Katalóg hier',
    }
 
    return render(request, 'core/hra_list.html', context)


def hra_detail_view(request, hra_id):
    """Zobrazí detaily jednej hry na základe jej ID."""
    
    hra = get_object_or_404(Hra, id=hra_id)
    
    context = {
        'hra': hra
    }
    return render(request, 'core/hra_detail.html', context)


def udalost_list_view(request):
    """Zobrazí zoznam všetkých dostupných udalostí."""
    
    vsetky_udalosti = Udalost.objects.all().order_by('datum_konania')
    
    context = {
        'udalosti': vsetky_udalosti,
    }
    
    return render(request, 'core/udalost_list.html', context)


def register_view(request):
    """Zobrazí a spracuje registračný formulár."""
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save() 
            return redirect('login') 
    else:
        form = CustomUserCreationForm()

    context = {
        'form': form,
        'nadpis': 'Registrácia nového používateľa',
    }
    
    return render(request, 'registration/register.html', context)