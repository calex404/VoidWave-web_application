# core/views.py (KOMPLETNÝ KÓD PRE STABILNÝ SERVER A FUNKČNOSŤ)

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

# core/views.py (Nahraď funkciu profil_detail_view)

def profil_detail_view(request, profil_id):
    profil = get_object_or_404(Profil, id=profil_id)
    
    # 1. Získame priateľov (accepted)
    priatelia = Priatelstvo.objects.filter(
        Q(profil1=profil) | Q(profil2=profil),
        stav='accepted'
    )
    # 2. Žiadosti (pre funkčnosť tlačidiel Accept/Reject)
    ziadosti = Priatelstvo.objects.filter(
        profil2=profil,
        stav='pending'
    )

    # 💥 FINAL FIX: NATVRDO VYPNEME PANEL OZNÁMENÍ 💥
    oznamenia_list = [] 
    
    context = {
        'profil': profil,
        'priatelia': priatelia,
        'ziadosti': ziadosti,
        'oznamenia_list': oznamenia_list # Posielame prázdny zoznam
    }
    return render(request, 'core/profil_detail.html', context)

# 💥 CHÝBAJÚCA FUNKCIA: PROFIL EDIT VIEW (Pridaná) 💥
def profil_edit_view(request):
    """Umožňuje prihlásenému používateľovi editovať vlastný profil (nickname a bio)."""
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    profil = request.user.profil 
    
    if request.method == 'POST':
        # Spracovanie odoslaných dát
        form = ProfilEditForm(request.POST, instance=profil)
        if form.is_valid():
            form.save()
            return redirect('profil_detail', profil_id=profil.id) 
    else:
        # Zobrazenie formulára s existujúcimi dátami
        form = ProfilEditForm(instance=profil)

    context = {
        'form': form,
        'profil': profil 
    }
    return render(request, 'core/profil_edit.html', context)

def send_friend_request(request, profil_id):
    """Odošle žiadosť o priateľstvo inému profilu s vynútenou diagnostikou."""
    if not request.user.is_authenticated:
        return redirect('login')
    
    from_profil = request.user.profil
    to_profil = get_object_or_404(Profil, id=profil_id)
    
    # Zabránenie odoslania samému sebe
    if from_profil == to_profil:
        return redirect('profil_detail', profil_id=profil_id)

    # 1. Kontrola, či už žiadosť alebo priateľstvo neexistuje
    friendship_exists = Priatelstvo.objects.filter(
        Q(profil1=from_profil, profil2=to_profil) | 
        Q(profil1=to_profil, profil2=from_profil)
    ).exists()
    
    if not friendship_exists:
        try:
            # 2. Vytvorenie záznamu Priatelstvo
            Priatelstvo.objects.create(
                profil1=from_profil,
                profil2=to_profil,
                stav='pending'
            )
            
            # 3. Vytvorenie Oznamenia pre príjemcu
            oznamenie = Oznamenie.objects.create(
                nazov='Nová žiadosť o priateľstvo',
                typ='sprava',
                obsah=f"{request.user.profil.nickname} ti poslal/a žiadosť o priateľstvo. Choď na svoj profil a prijmi ju!"
            )
            # 4. Vytvorenie Odoslania
            Odoslanie.objects.create(oznamenie=oznamenie, prijemca=to_profil)

            print("\n✅ INFO: Žiadosť a notifikácia ÚSPEŠNE VYTVORENÁ\n")

        except Exception as e:
            # 💥 TOTO NÁM POVIE, ČO NEFUNGUJE 💥
            print("\n🛑 FATALNA CHYBA PRI UKLADANÍ ŽIADOSTI/NOTIFIKÁCIE 🛑")
            print(f"CHYBA: {e}")
            print("----------------------------------------------------\n")

    # Vráti nás späť na profil, kde sme klikli
    return redirect('profil_detail', profil_id=profil_id)

def accept_friend_request(request, request_id):
    """Prijme žiadosť o priateľstvo a pošle notifikáciu."""
    print("ne")
    if not request.user.is_authenticated: return redirect('login')
    friendship = get_object_or_404(Priatelstvo, id=request_id)
    
    if friendship.profil2 == request.user.profil:
        friendship.stav = 'accepted'
        friendship.save()
        
        # Oznámenie pre odosielateľa
        oznamenie = Oznamenie.objects.create(nazov='Priateľstvo prijaté', typ='sprava', obsah=f"{request.user.profil.nickname} prijal tvoju žiadosť o priateľstvo. Ste teraz priatelia!")
        Odoslanie.objects.create(oznamenie=oznamenie, prijemca=friendship.profil1)

    # 💥 Vracia sa na zoznam oznámení 💥
    return redirect('oznamenie_list') 

def reject_friend_request(request, request_id):
    """Zamietne žiadosť o priateľstvo a pošle notifikáciu."""
    if not request.user.is_authenticated: return redirect('login')
    friendship = get_object_or_404(Priatelstvo, id=request_id)
    
    if friendship.profil2 == request.user.profil:
        # Oznámenie pre odosielateľa
        oznamenie = Oznamenie.objects.create(nazov='Žiadosť zamietnutá', typ='sprava', obsah=f"{request.user.profil.nickname} zamietol tvoju žiadosť o priateľstvo.")
        Odoslanie.objects.create(oznamenie=oznamenie, prijemca=friendship.profil1)
        friendship.delete()

    # 💥 Vracia sa na zoznam oznámení 💥
    return redirect('oznamenie_list')

def hra_list_view(request):
    vsetky_hry = Hra.objects.all()
    context = { 'hry': vsetky_hry, 'nadpis': 'Katalóg hier', }
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
    if not request.user.is_authenticated: return redirect('login')
    if not (request.user.is_superuser or request.user.profil.rola.nazov_role == 'Organizátor'): return redirect('udalost_list')

    if request.method == 'POST':
        form = UdalostForm(request.POST)
        if form.is_valid():
            nova_udalost = form.save(commit=False)
            nova_udalost.organizator = request.user.profil 
            nova_udalost.save()
            return redirect('udalost_list')
    else: form = UdalostForm()
    context = { 'form': form, 'nadpis': 'Vytvoriť novú udalosť' }
    return render(request, 'core/udalost_form.html', context)

def udalost_join_view(request, udalost_id):
    if not request.user.is_authenticated: return redirect('login')
    udalost = get_object_or_404(Udalost, id=udalost_id)
    profil = request.user.profil
    udalost.ucastnici.add(profil)
    return redirect('udalost_list')

def udalost_withdraw_view(request, udalost_id):
    if not request.user.is_authenticated: return redirect('login')
    udalost = get_object_or_404(Udalost, id=udalost_id)
    profil = request.user.profil
    udalost.ucastnici.remove(profil)
    return redirect('udalost_list')

def tim_list_view(request):
    vsetky_timy = Tim.objects.all()
    context = {'timy': vsetky_timy}
    return render(request, 'core/tim_list.html', context)

def tim_create_view(request):
    if not request.user.is_authenticated: return redirect('login')
    if Tim.objects.filter(clenovia=request.user.profil).exists(): return redirect('tim_list') 

    if request.method == 'POST':
        form = TimForm(request.POST)
        if form.is_valid():
            novy_tim = form.save()
            novy_tim.clenovia.add(request.user.profil)
            novy_tim.save()
            return redirect('tim_list')
    else: form = TimForm()

    context = { 'form': form, 'nadpis': 'Založiť nový tím' }
    return render(request, 'core/tim_form.html', context)

def tim_join_view(request, tim_id):
    if not request.user.is_authenticated: return redirect('login')
    tim = get_object_or_404(Tim, id=tim_id)
    profil = request.user.profil
    if Tim.objects.filter(clenovia=profil).exists(): return redirect('tim_list') 
    if tim.clenovia.count() >= MAX_TEAM_SIZE: return redirect('tim_list') 
    tim.clenovia.add(profil)
    return redirect('tim_list')

def rebricek_list_view(request):
    vsetky_rebricky = Rebricek.objects.all().order_by('-datum_aktualizacie')
    context = {'rebricky': vsetky_rebricky}
    return render(request, 'core/rebricek_list.html', context)

# core/views.py (Nahraď len funkciu oznamenie_list_view)

# core/views.py (Nahraď len funkciu oznamenie_list_view)

# core/views.py (Nahraď len funkciu oznamenie_list_view)

# core/views.py (Nahraď len funkciu oznamenie_list_view)

def oznamenie_list_view(request):
    """Zobrazí všetky oznámenia, žiadosti a pripomienky pre aktuálneho používateľa."""
    if not request.user.is_authenticated:
        return redirect('login')
    
    profil = request.user.profil
    
    # 1. ŽIADOSTI O PRIATEĽSTVO (Incoming Requests)
    ziadosti = Priatelstvo.objects.filter(profil2=profil, stav='pending')

    # 2. VŠEOBECNÉ NOTIFIKÁCIE (HISTÓRIA)
    # Načítame podľa dátumu odoslania (Krok 94 fix)
    odoslania = Odoslanie.objects.filter(prijemca=profil).order_by('-datum_odoslania')[:30]
    
    # 3. PRIPOMIENKY UDALOSTÍ (Reminders - Zjednodušená verzia)
    today = datetime.now().date()
    pripomienky = Udalost.objects.filter(ucastnici=profil, datum_konania__gte=today).order_by('datum_konania')

    oznamenia_historia = []
    # 💥 Vytvorenie kontextu pre šablónu 💥
    for o in odoslania:
        oznamenia_historia.append({
            'oznamenie': o.oznamenie,
            'datum_odoslania': o.datum_odoslania, 
            'datum_precitania': o.datum_precitania
        })

    context = {
        'odoslania_list': oznamenia_historia,
        'ziadosti_priatelstva': ziadosti, 
        'pripomienky': pripomienky,
    }
    return render(request, 'core/oznamenie_list.html', context)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save() 
            return redirect('login') 
    else: form = CustomUserCreationForm()
    context = { 'form': form, 'nadpis': 'Registrácia nového používateľa', }
    return render(request, 'registration/register.html', context)