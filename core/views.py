# core/views.py (KONSOLIDOVANÝ A OPRAVENÝ KÓD)

from django.shortcuts import render, get_object_or_404, redirect
from .models import Profil, Hra, Udalost, Tim, Rebricek, Oznamenie, Priatelstvo, Odoslanie
from .forms import CustomUserCreationForm, UdalostForm, TimForm, ProfilEditForm 
from datetime import datetime
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q

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

# core/views.py (Nahraď TÚTO FUNKCIU)

def profil_detail_view(request, profil_id):
    profil = get_object_or_404(Profil, id=profil_id)
    
    # 1. Získame priateľov a žiadosti
    priatelia = Priatelstvo.objects.filter(
        Q(profil1=profil) | Q(profil2=profil),
        stav='accepted'
    )
    ziadosti = Priatelstvo.objects.filter(
        profil2=profil,
        stav='pending'
    )

    # 2. 💥 OPRAVENÉ ZÍSKANIE NOTIFIKÁCIÍ 💥
    oznamenia_list = []
    if request.user.profil == profil:
        # Načítame všetky záznamy Odoslanie, kde je príjemca aktuálny profil.
        # DÔLEŽITÉ: Zoradíme podľa novo pridaného poľa 'datum_odoslania'.
        odoslania = Odoslanie.objects.filter(prijemca=profil).order_by('-datum_odoslania')
        
        for o in odoslania:
            oznamenia_list.append({
                # Odoslanie obsahuje Oznamenie aj dáta pre zobrazenie
                'oznamenie': o.oznamenie,
                'datum_odoslania': o.datum_odoslania, # Používame dáta z Odoslania
                'datum_precitania': o.datum_precitania
            })

    context = {
        'profil': profil,
        'priatelia': priatelia,
        'ziadosti': ziadosti,
        'oznamenia_list': oznamenia_list # Posielame notifikácie do šablóny
    }
    return render(request, 'core/profil_detail.html', context)

def profil_edit_view(request):
    """Umožňuje prihlásenému používateľovi editovať vlastný profil (nickname a bio)."""
    if not request.user.is_authenticated:
        return redirect('login')

    profil = request.user.profil 

    if request.method == 'POST':
        form = ProfilEditForm(request.POST, instance=profil)
        if form.is_valid():
            form.save()
            return redirect('profil_detail', profil_id=profil.id) 
    else:
        form = ProfilEditForm(instance=profil)

    context = {
        'form': form,
        'profil': profil 
    }
    return render(request, 'core/profil_edit.html', context)


# --- PRIATEĽSTVÁ ---

def accept_friend_request(request, request_id):
    """Prijme žiadosť o priateľstvo a pošle notifikáciu."""
    if not request.user.is_authenticated:
        return redirect('login')

    friendship = get_object_or_404(Priatelstvo, id=request_id)
    
    if friendship.profil2 == request.user.profil:
        friendship.stav = 'accepted'
        friendship.save()
        
        # --- NOTIFIKÁCIA PRE ODOSIELATEĽA ---
        oznamenie = Oznamenie.objects.create(
            nazov='Priateľstvo prijaté',
            typ='sprava',
            obsah=f"{request.user.profil.nickname} prijal tvoju žiadosť o priateľstvo. Ste teraz priatelia!"
        )
        Odoslanie.objects.create(oznamenie=oznamenie, prijemca=friendship.profil1)

    return redirect('profil_detail', profil_id=request.user.profil.id)


def reject_friend_request(request, request_id):
    """Zamietne žiadosť o priateľstvo a pošle notifikáciu."""
    if not request.user.is_authenticated:
        return redirect('login')

    friendship = get_object_or_404(Priatelstvo, id=request_id)
    
    if friendship.profil2 == request.user.profil:
        # --- NOTIFIKÁCIA PRE ODOSIELATEĽA ---
        oznamenie = Oznamenie.objects.create(
            nazov='Žiadosť zamietnutá',
            typ='sprava',
            obsah=f"{request.user.profil.nickname} zamietol tvoju žiadosť o priateľstvo."
        )
        Odoslanie.objects.create(oznamenie=oznamenie, prijemca=friendship.profil1)
        
        # Zmažeme záznam o žiadosti
        friendship.delete()

    return redirect('profil_detail', profil_id=request.user.profil.id)


# --- HRY, UDALOSTI, TÍMY, OSTATNÉ (Kód je rovnaký, ale je čistý a na konci) ---

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

def udalost_join_view(request, udalost_id):
    """Pridá aktuálneho používateľa ako účastníka na udalosť."""
    if not request.user.is_authenticated:
        return redirect('login')
    udalost = get_object_or_404(Udalost, id=udalost_id)
    profil = request.user.profil
    udalost.ucastnici.add(profil)
    return redirect('udalost_list')

def udalost_withdraw_view(request, udalost_id):
    """Odstráni aktuálneho používateľa zo zoznamu účastníkov."""
    if not request.user.is_authenticated:
        return redirect('login')
    udalost = get_object_or_404(Udalost, id=udalost_id)
    profil = request.user.profil
    udalost.ucastnici.remove(profil)
    return redirect('udalost_list')


def tim_list_view(request):
    vsetky_timy = Tim.objects.all()
    context = {'timy': vsetky_timy}
    return render(request, 'core/tim_list.html', context)

def tim_create_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if Tim.objects.filter(clenovia=request.user.profil).exists():
        return redirect('tim_list') 

    if request.method == 'POST':
        form = TimForm(request.POST)
        if form.is_valid():
            novy_tim = form.save()
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
    
    if Tim.objects.filter(clenovia=profil).exists():
        return redirect('tim_list') 
        
    if tim.clenovia.count() >= MAX_TEAM_SIZE:
        return redirect('tim_list') 
    
    tim.clenovia.add(profil)
    return redirect('tim_list')

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