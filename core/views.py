# core/views.py (OPRAVENÉ IMPORTY)

from django.shortcuts import render, get_object_or_404, redirect
from .models import Profil, Hra, Udalost, Tim, Rebricek, Oznamenie, Priatelstvo, Odoslanie, Hodnotenie 
from .forms import CustomUserCreationForm, UdalostForm, TimForm, ProfilEditForm, HodnotenieForm
from datetime import datetime, timedelta
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q, Avg, Count
from django.contrib import messages
from django.utils import timezone
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

# core/views.py (Nahraď TÚTO funkciu)

def profil_detail_view(request, profil_id):
    profil = get_object_or_404(Profil, id=profil_id)
    
    # Získame priateľov a žiadosti (logika ostáva)
    priatelia = Priatelstvo.objects.filter(
        Q(profil1=profil) | Q(profil2=profil),
        stav='accepted'
    )
    ziadosti = Priatelstvo.objects.filter(
        profil2=profil,
        stav='pending'
    )

    # Získanie notifikácií (Len ak pozerám SVOJ profil) 
    oznamenia_list = []
    if request.user.profil == profil:
        # Načítame záznamy, zoradené podľa dátumu odoslania
        odoslania = Odoslanie.objects.filter(prijemca=profil).order_by('-datum_odoslania') 
        for o in odoslania:
            oznamenia_list.append({
                'oznamenie': o.oznamenie,
                'datum_odoslania': o.datum_odoslania,
                'datum_precitania': o.datum_precitania
            })

    context = {
        'profil': profil,
        'priatelia': priatelia,
        'ziadosti': ziadosti,
        'oznamenia_list': oznamenia_list
    }
    # TOTO renderuje správnu šablónu s profilom
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

# core/views.py (Nahraď len funkciu send_friend_request)

def send_friend_request(request, profil_id):
    """Odošle žiadosť o priateľstvo inému profilu."""
    if not request.user.is_authenticated: return redirect('login')
    
    from_profil = request.user.profil
    to_profil = get_object_or_404(Profil, id=profil_id)
    
    if from_profil == to_profil:
        # Ak si posielam sám sebe, presmerujem na vlastný profil
        return redirect('profil_detail', profil_id=from_profil.id)
        
    # 1. Kontrola, či už žiadosť alebo priateľstvo neexistuje
    friendship_exists = Priatelstvo.objects.filter(
        Q(profil1=from_profil, profil2=to_profil) | 
        Q(profil1=to_profil, profil2=from_profil)
    ).exists()
    
    if not friendship_exists:
        # 2. Vytvorenie záznamu Priatelstvo
        Priatelstvo.objects.create(
            profil1=from_profil,
            profil2=to_profil,
            stav='pending'
        )
        
        # 3. Oznámenie pre príjemcu
        oznamenie = Oznamenie.objects.create(
            nazov='Nová žiadosť o priateľstvo',
            typ='sprava',
            obsah=f"{request.user.profil.nickname} ti poslal/a žiadosť o priateľstvo. Choď na svoj profil a prijmi ju!"
        )
        Odoslanie.objects.create(oznamenie=oznamenie, prijemca=to_profil)

    # 💥 FIX: Vrátime ťa na SVOJ vlastný profil 💥
    return redirect('profil_detail', profil_id=from_profil.id)

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

# core/views.py (Nahraď existujúcu funkciu)

from django.utils import timezone  # <--- Dôležitý import

def udalost_list_view(request):
    """Zobrazuje LEN budúce udalosti (odteraz dopredu)"""
    now = timezone.now()
    # gte = Greater Than or Equal (Väčšie alebo rovné = Budúcnosť)
    udalosti = Udalost.objects.filter(datum_konania__gte=now).order_by('datum_konania')
    
    return render(request, 'core/udalost_list.html', {'udalosti': udalosti})

def udalost_archiv_view(request):
    now = timezone.now()
    
    # Filtrujeme všetko, čo je MENŠIE (lt) ako teraz = MINULOSŤ
    archivne_udalosti = Udalost.objects.filter(datum_konania__lt=now).order_by('-datum_konania')
    
    # DEBUG VÝPIS (Uvidíš ho v termináli, keď refreshneš stránku)
    print(f"--- DEBUG ARCHÍV ---")
    print(f"Aktuálny čas: {now}")
    print(f"Nájdených udalostí v archíve: {archivne_udalosti.count()}")
    
    context = {
        'archiv': archivne_udalosti  # <--- TOTO SLOVO JE KĽÚČOVÉ
    }
    return render(request, 'core/udalost_archive.html', context)

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

def rebricky_view(request):
    now = timezone.now()
    
    # 1. DENNÝ REBRÍČEK (Udalosti za posledných 24 hodín)
    denny_limit = now - timedelta(days=1)
    top_denne = Profil.objects.filter(prihlasene_udalosti__datum_konania__gte=denny_limit)\
        .annotate(score=Count('prihlasene_udalosti'))\
        .order_by('-score')[:5]

    # 2. TÝŽDENNÝ REBRÍČEK (Udalosti za posledných 7 dní)
    tyzdenny_limit = now - timedelta(days=7)
    top_tyzdenne = Profil.objects.filter(prihlasene_udalosti__datum_konania__gte=tyzdenny_limit)\
        .annotate(score=Count('prihlasene_udalosti'))\
        .order_by('-score')[:5]

    # 3. MESAČNÝ REBRÍČEK (Udalosti za posledných 30 dní)
    mesacny_limit = now - timedelta(days=30)
    top_mesacne = Profil.objects.filter(prihlasene_udalosti__datum_konania__gte=mesacny_limit)\
        .annotate(score=Count('prihlasene_udalosti'))\
        .order_by('-score')[:5]

    context = {
        'top_denne': top_denne,
        'top_tyzdenne': top_tyzdenne,
        'top_mesacne': top_mesacne,
    }
    
    return render(request, 'core/rebricek_list.html', context)

def oznamenie_list_view(request):
    """Zobrazí všetky oznámenia, žiadosti a pripomienky pre aktuálneho používateľa."""
    if not request.user.is_authenticated:
        return redirect('login')
    
    profil = request.user.profil
    
    # --- MARK AS READ LOGIC (Kľúčové pre zmiznutie zvončeka) ---
    # Získame všetky neprečítané oznámenia pre aktuálneho používateľa a označíme ich ako prečítané
    Odoslanie.objects.filter(prijemca=profil, stav='neprecitane').update(stav='precitane', datum_precitania=datetime.now())
    # -----------------------------------------------------------

    # 1. ŽIADOSTI O PRIATEĽSTVO (Incoming Requests)
    ziadosti = Priatelstvo.objects.filter(profil2=profil, stav='pending')

    # 2. VŠEOBECNÉ NOTIFIKÁCIE (História)
    # Načítame znova, tentokrát už ako prečítané
    odoslania = Odoslanie.objects.filter(prijemca=profil).order_by('-datum_odoslania')[:30]
    
    # 3. PRIPOMIENKY UDALOSTÍ (Reminders)
    today = datetime.now().date()
    pripomienky = Udalost.objects.filter(ucastnici=profil, datum_konania__gte=today).order_by('datum_konania')

    oznamenia_historia = []
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

# core/views.py (Pridaj k ostatným View funkciám)

# core/views.py (Pridaj TÚTO FUNKCIU k ostatným View funkciám)


# core/views.py (Pridaj na koniec súboru)
from .forms import HodnotenieForm # Uisti sa, že máš tento import hore

# core/views.py (Nahraď existujúcu funkciu udalost_archiv_view)
# core/views.py (Nahraď existujúcu funkciu udalost_archiv_view)

# core/views.py (Nahraď existujúcu funkciu hodnotenie_create_view)

# core/views.py (Nahraď existujúcu funkciu hodnotenie_create_view)

def hodnotenie_create_view(request, udalost_id):
    """Spracuje odoslanie hodnotenia k danej udalosti s kontrolou účasti."""
    from django.contrib import messages
    
    if not request.user.is_authenticated:
        return redirect('login')

    udalost = get_object_or_404(Udalost, id=udalost_id)
    profil = request.user.profil
    print(f"0. Udalost chuju (DB Check): {udalost}")
    realni_ucastnici = udalost.ucastnici.all()
    print(f"Počet účastníků v DB: {realni_ucastnici.count()}")
    print("Seznam jmen účastníků:")
    for u in realni_ucastnici:
        print(f" - ID: {u.id}, Nick: {u.nickname}")
    # --- DIAGNOSTIKA ID ---
    print(f"\n--- DEBUG RATING CHECK ---")
    print(f"1. Logged in Profile ID: {profil.id}")
    print(f"2. Target Event ID: {udalost_id}")
    print(f"3. Udalost.ucastnici IDs: {[p.id for p in udalost.ucastnici.all()]}")
    
    # KONTROLA POVOLENIA: Hodnotiť môže len ten, kto sa zúčastnil
    is_participant = udalost.ucastnici.filter(id=profil.id).exists()
    print(f"4. Is Participant (DB Check): {is_participant}")
    print(f"--- END DEBUG ---\n")
    
    if not is_participant:
        # TENTO BLOK STÁLE HÁDŽE CHYBU
        messages.error(request, f"Hodnotenie udalosti '{udalost.nazov}' môže udeliť len prihlásený účastník.")
        return redirect('udalost_archiv') 
    if request.method == 'POST':
        # Keď klikneš na tlačidlo "Uložiť Hodnotenie"
        form = HodnotenieForm(request.POST)
        if form.is_valid():
            hodnotenie = form.save(commit=False)
            hodnotenie.udalost = udalost  # Priradíme udalosť
            hodnotenie.profil = profil     # Priradíme teba ako autora
            hodnotenie.save()
            
            messages.success(request, "Hodnotenie úspešne pridané!")
            return redirect('udalost_archiv') # Po uložení ťa hodí späť na archív
    else:
        # Ak len prišiel na stránku (GET request) -> zobrazíme prázdny formulár
        form = HodnotenieForm()

    # TOTO TI CHÝBALO: Nakoniec musíme vrátiť šablónu (HTML)
    context = {
        'form': form,
        'udalost': udalost,
        'profil': profil,
        'profil_id': profil.id
    }
    return render(request, 'core/hodnotenie_create.html', {'form': form, 'udalost': udalost})
    
    # --- Spracovanie Formulára ---
    # ... (zvyšok logiky zostáva)