# core/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Profil, Hra, Udalost, Tim, Rebricek, Oznamenie
# 💥 DÔLEŽITÉ: Pridaný import TimForm
from .forms import CustomUserCreationForm, UdalostForm, TimForm 
from datetime import datetime
from django.contrib.auth.forms import AuthenticationForm

# Konštanta pre maximálny počet členov tímu
MAX_TEAM_SIZE = 5

# --- ÚVOD A PROFILY ---

def home_view(request):
    context = {}
    if not request.user.is_authenticated:
        context['form'] = AuthenticationForm()
    return render(request, 'core/home.html', context)

def profil_list_view(request):
    vsetky_profily = Profil.objects.all()
    context = {
        'profily': vsetky_profily,
        'datum_a_cas': datetime.now()
    }
    return render(request, 'core/profil_list.html', context)
# core/views.py (Pridaj k ostatným View funkciám)

# core/views.py (Pridaj k ostatným View funkciám)

def profil_detail_view(request, profil_id):
    """Zobrazí detaily jedného profilu na základe jeho ID."""
    # Používame Profil, nie User, lebo Profil obsahuje rolu a bio
    profil = get_object_or_404(Profil, id=profil_id)
    context = {'profil': profil}
    return render(request, 'core/profil_detail.html', context)

# ... (ostatné View funkcie pokračujú)
# --- HRY ---

def hra_list_view(request):
    vsetky_hry = Hra.objects.all()
    context = {
        'hry': vsetky_hry,
        'nadpis': 'Katalóg hier',
    }
    return render(request, 'core/hra_list.html', context)

def hra_detail_view(request, hra_id):
    hra = get_object_or_404(Hra, id=hra_id)
    context = {'hra': hra}
    return render(request, 'core/hra_detail.html', context)

# --- UDALOSTI ---

def udalost_list_view(request):
    vsetky_udalosti = Udalost.objects.all().order_by('datum_konania')
    context = {'udalosti': vsetky_udalosti}
    return render(request, 'core/udalost_list.html', context)

def udalost_create_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not (request.user.is_superuser or request.user.profil.rola.nazov_role == 'Organizátor'):
        return redirect('udalost_list')

    if request.method == 'POST':
        form = UdalostForm(request.POST)
        if form.is_valid():
            nova_udalost = form.save(commit=False)
            nova_udalost.organizator = request.user.profil 
            nova_udalost.save()
            return redirect('udalost_list')
    else:
        form = UdalostForm()

    context = {
        'form': form,
        'nadpis': 'Vytvoriť novú udalosť'
    }
    return render(request, 'core/udalost_form.html', context)

# --- TÍMY ---

def tim_list_view(request):
    vsetky_timy = Tim.objects.all()
    context = {'timy': vsetky_timy}
    return render(request, 'core/tim_list.html', context)

def tim_create_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # KONTROLA 1: Nemôže založiť, ak už je v nejakom tíme
    if Tim.objects.filter(clenovia=request.user.profil).exists():
        return redirect('tim_list') 

    if request.method == 'POST':
        form = TimForm(request.POST)
        if form.is_valid():
            novy_tim = form.save()
            # Automaticky pridáme zakladateľa ako člena
            novy_tim.clenovia.add(request.user.profil)
            novy_tim.save()
            return redirect('tim_list')
    else:
        form = TimForm()

    context = {
        'form': form,
        'nadpis': 'Založiť nový tím'
    }
    return render(request, 'core/tim_form.html', context)

def tim_join_view(request, tim_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    tim = get_object_or_404(Tim, id=tim_id)
    profil = request.user.profil
    
    # KONTROLA 1: Nemôže sa pridať, ak už je v inom tíme
    if Tim.objects.filter(clenovia=profil).exists():
        return redirect('tim_list') 
        
    # KONTROLA 2: Tím je plný
    if tim.clenovia.count() >= MAX_TEAM_SIZE:
        return redirect('tim_list') 
    
    tim.clenovia.add(profil)
    return redirect('tim_list')

# --- OSTATNÉ ---

def rebricek_list_view(request):
    vsetky_rebricky = Rebricek.objects.all().order_by('-datum_aktualizacie')
    context = {'rebricky': vsetky_rebricky}
    return render(request, 'core/rebricek_list.html', context)

def oznamenie_list_view(request):
    vsetky_oznamenia = Oznamenie.objects.all().order_by('-datum_vytvorenia')
    context = {'oznamenia': vsetky_oznamenia}
    return render(request, 'core/oznamenie_list.html', context)

def register_view(request):
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