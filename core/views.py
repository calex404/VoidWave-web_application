# core/views.py (OPRAVENÉ IMPORTY)

from django.shortcuts import render, get_object_or_404, redirect
from .models import Profil, Hra, Udalost, Tim, Rebricek, Oznamenie, Priatelstvo, Odoslanie, Hodnotenie, FriendRequest
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

# core/views.py

def profil_list_view(request):
    """1. ČISTÝ ZOZNAM (Len na pozeranie - bez tlačidiel)"""
    profily = Profil.objects.all()
    context = {
        'profily': profily,
        'hladame_priatelov': False  # <--- Tlačidlá skryté
    }
    return render(request, 'core/profil_list.html', context)

def find_priatelov_view(request):
    """2. HĽADANIE (Zoznam s tlačidlami 'Pridať') - Vylučuje existujúcich priateľov."""
    if not request.user.is_authenticated:
        return redirect('login')

    hladany_profil = request.user.profil
    
    # --- 1. Zostavíme zoznam ID priateľov a vlastného ID ---
    
    # Nájdi všetky POTVRDENÉ vzťahy, kde figuruje aktuálny profil
    priatelia_vztahy = Priatelstvo.objects.filter(
        Q(profil1=hladany_profil) | Q(profil2=hladany_profil),
        stav='accepted'
    )
    
    # Vytvoríme list ID na vylúčenie (vrátane vlastného ID)
    priatelia_ids = [hladany_profil.id]
    for vztah in priatelia_vztahy:
        # Určíme, kto je ten druhý a pridáme ho do listu
        if vztah.profil1 == hladany_profil:
            priatelia_ids.append(vztah.profil2.id)
        else:
            priatelia_ids.append(vztah.profil1.id)
            
    # 2. Vylúčime priateľov a mňa zo zoznamu výsledkov
    profily = Profil.objects.all().exclude(id__in=priatelia_ids)
    
    context = {
        'profily': profily,
        'hladame_priatelov': True,  # Zobrazí tlačidlá v HTML
    }
    return render(request, 'core/profil_list.html', context)

# core/views.py (Nahraď funkciu profil_detail_view)

# core/views.py (Nahraď TÚTO funkciu)

def profil_detail_view(request, profil_id):
    profil = get_object_or_404(Profil, id=profil_id)
    
    # 1. Nájdi všetky vzťahy, kde figuruje tento profil (priatelia aj čakajúci)
    vsetky_vztahy = Priatelstvo.objects.filter(
        Q(profil1=profil) | Q(profil2=profil) 
    )
    
    # 2. Vyfiltruj len tie, ktoré sú POTVRDENÉ
    priatelia = vsetky_vztahy.filter(stav='accepted')
    
    # --- FINÁLNY DEBUG CHECK ---
    print(f"\n--- ZOBRAZENIE PRIATEĽOV ---")
    print(f"Hľadaný profil: {profil.nickname}")
    print(f"NAŠLO V DB (prijatých): {priatelia.count()}")
    print("---------------------------\n")

    context = {
        'profil': profil,
        'priatelia': priatelia, # Toto posielame do HTML
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

# core/views.py (Nahraď len funkciu send_friend_request)

def send_friend_request(request, profil_id):
    """
    Hybridná verzia: Robí staré notifikácie (správy) AJ nové (čísielko) 
    a správne presmeruje.
    """
    if not request.user.is_authenticated: return redirect('login')
    
    from_profil = request.user.profil
    to_profil = get_object_or_404(Profil, id=profil_id)
    
    if from_profil == to_profil:
        return redirect('profil_detail', profil_id=from_profil.id)
        
    # 1. Kontrola, či už nie sú priatelia (Stará logika)
    friendship_exists = Priatelstvo.objects.filter(
        Q(profil1=from_profil, profil2=to_profil) | 
        Q(profil1=to_profil, profil2=from_profil)
    ).exists()
    
    if not friendship_exists:
        # A) Vytvoríme záznam v Priatelstvo (Stará logika)
        Priatelstvo.objects.create(
            profil1=from_profil,
            profil2=to_profil,
            stav='pending'
        )
        
        # B) Pošleme textovú správu do Oznámení (Stará logika)
        oznamenie = Oznamenie.objects.create(
            nazov='Nová žiadosť o priateľstvo',
            typ='sprava',
            obsah=f"{request.user.profil.nickname} ti poslal/a žiadosť o priateľstvo."
        )
        Odoslanie.objects.create(oznamenie=oznamenie, prijemca=to_profil)

        # C) Vytvoríme záznam pre ČERVENÉ ČÍSIELKO (Nová logika)
        FriendRequest.objects.get_or_create(od_koho=from_profil, pre_koho=to_profil)

    # D) OPRAVA PRESMEROVANIA: Vráti ťa na zoznam s tlačidlami
    return redirect('find_priatelov')

def accept_friend_request(request, request_id):
    """Prijme žiadosť, vytvorí/opraví Priateľstvo a zmaže notifikáciu."""
    if not request.user.is_authenticated: return redirect('login')
    
    ziadost = get_object_or_404(FriendRequest, id=request_id)
    
    if ziadost.pre_koho == request.user.profil:
        
        # 1. Zoraď profily podľa ID, aby sme našli existujúci záznam v Priatelstvo
        p1, p2 = sorted([ziadost.od_koho, ziadost.pre_koho], key=lambda x: x.id)
        
        # 2. Nájdeme alebo vytvoríme záznam v Priatelstvo a nastavíme ho na 'accepted'
        
        # AK už existuje pending záznam (čo by sa nemalo stať, ale pre istotu)
        priatelstvo_obj, created = Priatelstvo.objects.get_or_create(
            profil1=p1, 
            profil2=p2, 
            # defaults sa použije len pri created=True
            defaults={'stav': 'accepted'} 
        )
        
        # AK bol nájdený (created=False), alebo AK bol práve vytvorený a má stav 'pending', aktualizujeme ho
        if priatelstvo_obj.stav != 'accepted':
             priatelstvo_obj.stav = 'accepted'
             priatelstvo_obj.save()
        
        # 3. Zmažeme žiadosť (notifikáciu)
        ziadost.delete()

        messages.success(request, f"Teraz si priateľ s {ziadost.od_koho.nickname}!")

    # Vrátime sa do Oznámení
    return redirect('oznamenie_list')

def reject_friend_request(request, request_id):
    """Zamietne žiadosť a vyčistí všetko."""
    if not request.user.is_authenticated: return redirect('login')
    
    old_friendship = get_object_or_404(Priatelstvo, id=request_id)
    
    if old_friendship.profil2 == request.user.profil:
        # Pošleme správu o zamietnutí
        oznamenie = Oznamenie.objects.create(
            nazov='Žiadosť zamietnutá', 
            typ='sprava', 
            obsah=f"{request.user.profil.nickname} zamietol tvoju žiadosť."
        )
        Odoslanie.objects.create(oznamenie=oznamenie, prijemca=old_friendship.profil1)
        
        # Zmažeme NOVÚ notifikáciu (červené čísielko)
        FriendRequest.objects.filter(
            od_koho=old_friendship.profil1, 
            pre_koho=request.user.profil
        ).delete()
        
        # Zmažeme STARÚ žiadosť
        old_friendship.delete()

    return redirect('profil_detail', profil_id=request.user.profil.id)

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
    """Zobrazí len relevantné notifikácie a vynuluje počítadlo."""
    if not request.user.is_authenticated: return redirect('login')
    
    profil = request.user.profil
    now = timezone.now()
    limit = now + timedelta(days=1) # Zajtra

    # 1. URGENTNÉ UDALOSTI (Len tie, kde som účastník a sú do 24h)
    moje_urgentne = Udalost.objects.filter(
        ucastnici=profil,           # <--- Kľúčový filter: Len moje
        datum_konania__gt=now,
        datum_konania__lte=limit
    ).order_by('datum_konania')

    # 2. ŽIADOSTI O PRIATEĽSTVO
    ziadosti = FriendRequest.objects.filter(pre_koho=profil)

    # --- RESETOVANIE ČÍSLA V MENU ---
    # Uložíme si aktuálny počet do session.
    # Context processor to porovná a ak sa to rovná, zobrazí 0.
    total_count = moje_urgentne.count() + ziadosti.count()
    request.session['videny_pocet_notifikacii'] = total_count

    context = {
        'moje_urgentne': moje_urgentne,
        'ziadosti': ziadosti,
    }
    return render(request, 'core/oznamenie_list.html', context)

from django.contrib.auth import login # <--- Pridaj tento import hore!

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Vytvoríme profil (aby nevznikla chyba neskôr)
            Profil.objects.get_or_create(user=user, defaults={'nickname': user.username})
            
            # --- ZMENA TU ---
            # Vyhodili sme login(request, user) -> užívateľ sa neprihlási sám
            
            # Pridáme správu pre užívateľa (voliteľné, ale fajn)
            messages.success(request, "Registrácia bola úspešná! Teraz sa môžeš prihlásiť.")
            
            # Presmerujeme na prihlasovaciu stránku
            return redirect('login') 
            
    else:
        form = CustomUserCreationForm()
        
    context = { 'form': form, 'nadpis': 'Registrácia nového používateľa' }
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

# core/views.py

def dashboard_view(request):
    if not request.user.is_authenticated: return redirect('login')
    
    # Už neposielame 'ziadosti', len profil
    return render(request, 'core/dashboard.html', {'profil': request.user.profil})