from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q, Avg, Count
from django.utils import timezone
from .models import (
    Profil, Hra, Udalost, Tim, Oznamenie, Priatelstvo, 
    Odoslanie, Hodnotenie, FriendRequest, Rola
)
from .forms import (
    CustomUserCreationForm, UdalostForm, TimForm, ProfilEditForm, HodnotenieForm
)


MAX_TEAM_SIZE = 5


def home_view(request):
    """
    Domovská stránka. Slúži ako login pre neprihlásených a welcome screen pre prihlásených.
    Spracováva POST požiadavky na prihlásenie (LoginView je presunutý sem).
    """
    form = AuthenticationForm()

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            return redirect('home') 
        else:
            messages.error(request, "Nesprávne meno alebo heslo.")

    context = {
        'form': form
    }
    return render(request, 'core/home.html', context)


def register_view(request):
    """Spracováva registráciu nového používateľa a automaticky vytvára profil."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            Profil.objects.get_or_create(user=user, defaults={'nickname': user.username})
            
            messages.success(request, "Registrácia bola úspešná! Teraz sa môžeš prihlásiť.")
            
            return redirect('home') 
            
    else:
        form = CustomUserCreationForm()
        
    context = { 'form': form, 'nadpis': 'Registrácia nového používateľa' }
    return render(request, 'registration/register.html', context)


def dashboard_view(request):
    """Zobrazí súkromný ovládací panel (Dashboard)."""
    if not request.user.is_authenticated:
        return redirect('login')
    
    profil = request.user.profil
    
    context = {
        'profil': profil,
    }
    return render(request, 'core/dashboard.html', context)


def profil_list_view(request):
    """Zobrazí čistý zoznam profilov (Directory)."""
    profily = Profil.objects.all()
    context = {
        'profily': profily,
        'hladame_priatelov': False  
    }
    return render(request, 'core/profil_list.html', context)


def find_priatelov_view(request):
    """
    Zobrazí zoznam profilov s tlačidlami 'Pridať'.
    Vylučuje mňa a všetkých, s ktorými už mám potvrdené priateľstvo.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    hladany_profil = request.user.profil
    
    priatelia_vztahy = Priatelstvo.objects.filter(
        Q(profil1=hladany_profil) | Q(profil2=hladany_profil),
        stav='accepted'
    )
    
    priatelia_ids = [hladany_profil.id]
    for vztah in priatelia_vztahy:
        if vztah.profil1 == hladany_profil:
            priatelia_ids.append(vztah.profil2.id)
        else:
            priatelia_ids.append(vztah.profil1.id)
            
    profily = Profil.objects.all().exclude(id__in=priatelia_ids)
    
    context = {
        'profily': profily,
        'hladame_priatelov': True,  
    }
    return render(request, 'core/profil_list.html', context)


def profil_detail_view(request, profil_id):
    """
    Zobrazí verejný detail profilu (Read-Only).
    """
    profil = get_object_or_404(Profil, id=profil_id)
    
    priatelia = Priatelstvo.objects.filter(
        Q(profil1=profil) | Q(profil2=profil),
        stav='accepted'
    )

    print(f"\n--- ZOBRAZENIE PRIATEĽOV ---")
    print(f"Hľadaný profil: {profil.nickname}")
    print(f"NAŠLO V DB (prijatých): {priatelia.count()}")
    print("---------------------------\n")

    context = {
        'profil': profil,
        'priatelia': priatelia,
    }
    return render(request, 'core/profil_detail.html', context)


def profil_edit_view(request):
    """Umožňuje prihlásenému používateľovi editovať vlastný profil."""
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    profil = request.user.profil 
    
    if request.method == 'POST':
        form = ProfilEditForm(request.POST, instance=profil)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil bol úspešne aktualizovaný.")
            return redirect('profil_detail', profil_id=profil.id) 
    else:
        form = ProfilEditForm(instance=profil)

    context = {
        'form': form,
        'profil': profil 
    }
    return render(request, 'core/profil_edit.html', context)


def send_friend_request(request, profil_id):
    """
    Odošle žiadosť (vytvorí FriendRequest) a vytvorí záznam v Priatelstvo s pending statusom.
    """
    if not request.user.is_authenticated: return redirect('login')

    from_profil = request.user.profil
    to_profil = get_object_or_404(Profil, id=profil_id)
    
    if request.method == 'POST':
        if from_profil == to_profil:
            return redirect('profil_detail', profil_id=from_profil.id)

        friendship_exists = Priatelstvo.objects.filter(
            Q(profil1=from_profil, profil2=to_profil) | 
            Q(profil1=to_profil, profil2=from_profil)
        ).exists()
        
        if not friendship_exists:
            Priatelstvo.objects.create(profil1=from_profil, profil2=to_profil, stav='pending')
            
            FriendRequest.objects.get_or_create(od_koho=from_profil, pre_koho=to_profil)

            oznamenie = Oznamenie.objects.create(
                nazov='Nová žiadosť o priateľstvo', typ='sprava',
                obsah=f"{request.user.profil.nickname} ti poslal/a žiadosť o priateľstvo."
            )
            Odoslanie.objects.create(oznamenie=oznamenie, prijemca=to_profil)
            
            messages.success(request, f"Žiadosť pre {to_profil.nickname} bola odoslaná!")

    return redirect('find_priatelov')


def accept_friend_request(request, request_id):
    """Prijme žiadosť, nájde existujúci Priatelstvo záznam a zmení stav na 'accepted'."""
    if not request.user.is_authenticated: return redirect('login')
    
    ziadost = get_object_or_404(FriendRequest, id=request_id)
    
    if ziadost.pre_koho == request.user.profil:
        
        p1, p2 = sorted([ziadost.od_koho, ziadost.pre_koho], key=lambda x: x.id)

        Priatelstvo.objects.filter(
            profil1=p1,
            profil2=p2,
            stav='pending'
        ).update(stav='accepted')

        ziadost.delete()

        messages.success(request, f"Teraz si priateľ s {ziadost.od_koho.nickname}!")

    return redirect('oznamenie_list')


def reject_friend_request(request, request_id):
    """Zamietne žiadosť a vyčistí všetky súvisiace záznamy."""
    if not request.user.is_authenticated: return redirect('login')
    
    old_friendship = get_object_or_404(Priatelstvo, id=request_id)
    
    if old_friendship.profil2 == request.user.profil:
        oznamenie = Oznamenie.objects.create(
            nazov='Žiadosť zamietnutá', typ='sprava', 
            obsah=f"{request.user.profil.nickname} zamietol tvoju žiadosť."
        )
        Odoslanie.objects.create(oznamenie=oznamenie, prijemca=old_friendship.profil1)
        
        FriendRequest.objects.filter(
            od_koho=old_friendship.profil1, 
            pre_koho=request.user.profil
        ).delete()
        
        old_friendship.delete()

    return redirect('profil_detail', profil_id=request.user.profil.id)


def hra_list_view(request):
    """Zobrazí katalóg všetkých hier."""
    vsetky_hry = Hra.objects.all()
    context = { 'hry': vsetky_hry, 'nadpis': 'Katalóg hier', }
    return render(request, 'core/hra_list.html', context)


def hra_detail_view(request, hra_id):
    """Zobrazí detail konkrétnej hry."""
    hra = get_object_or_404(Hra, id=hra_id)
    context = {'hra': hra}
    return render(request, 'core/hra_detail.html', context)


def udalost_list_view(request):
    """Zobrazuje LEN budúce udalosti (odteraz dopredu)"""
    now = timezone.now()
    udalosti = Udalost.objects.filter(datum_konania__gte=now).order_by('datum_konania')
    
    return render(request, 'core/udalost_list.html', {'udalosti': udalosti})


# core/views.py (Nahraď funkciu udalost_archiv_view)

def udalost_archiv_view(request):
    from django.db.models import Avg 
    from datetime import datetime
    
    now = datetime.now() 
    archiv_udalosti = Udalost.objects.filter(datum_konania__lt=now).order_by('-datum_konania')

    udalosti_s_hodnotenim = []
    current_profil = request.user.profil if request.user.is_authenticated else None
    
    for udalost in archiv_udalosti:
        # 1. Načítanie všetkých hodnotení
        vsetky_hodnotenia = Hodnotenie.objects.filter(udalost=udalost).order_by('-datum_hodnotenia') 
        
        # Výpočet priemeru (ak sú hodnotenia)
        if vsetky_hodnotenia.exists():
            priemer = vsetky_hodnotenia.aggregate(Avg('hodnotenie'))['hodnotenie__avg']
            priemer_hodnotou = round(priemer, 2)
        else:
            priemer_hodnotou = None
        
        # 2. 💥 KONTROLA: Už som hodnotil? 💥
        uz_som_hodnotil = False
        if current_profil:
             # Toto vráti True, ak už existuje záznam v DB
             uz_som_hodnotil = Hodnotenie.objects.filter(profil=current_profil, udalost=udalost).exists()
        
        udalosti_s_hodnotenim.append({
            'udalost': udalost,
            'uz_som_hodnotil': uz_som_hodnotil, # Posielame True/False do šablóny
            'priemer': priemer_hodnotou, 
            'vsetky_hodnotenia': vsetky_hodnotenia,
        })

    context = {'udalosti': udalosti_s_hodnotenim}
    return render(request, 'core/udalost_archive.html', context)


def udalost_create_view(request):
    """Vytvorenie novej udalosti (len pre organizátorov)."""
    if not request.user.is_authenticated: return redirect('login')
    if not (request.user.is_superuser or Rola.objects.filter(profil=request.user.profil, nazov_role='Organizátor').exists()):
        return redirect('udalost_list')

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
    """Prihlásenie na udalosť."""
    if not request.user.is_authenticated: return redirect('login')
    udalost = get_object_or_404(Udalost, id=udalost_id)
    profil = request.user.profil
    udalost.ucastnici.add(profil)
    return redirect('udalost_list')


def udalost_withdraw_view(request, udalost_id):
    """Odhlásenie z udalosti."""
    if not request.user.is_authenticated: return redirect('login')
    udalost = get_object_or_404(Udalost, id=udalost_id)
    profil = request.user.profil
    udalost.ucastnici.remove(profil)
    return redirect('udalost_list')


def hodnotenie_create_view(request, udalost_id):
    """Spracuje odoslanie hodnotenia k danej udalosti s kontrolou účasti."""
    from django.contrib import messages
    
    if not request.user.is_authenticated:
        return redirect('login')

    udalost = get_object_or_404(Udalost, id=udalost_id)
    profil = request.user.profil
    
    is_participant = udalost.ucastnici.filter(id=profil.id).exists()
    
    if not is_participant:
        messages.error(request, f"Hodnotenie udalosti '{udalost.nazov}' môže udeliť len prihlásený účastník.")
        return redirect('udalost_archiv') 
        
    if request.method == 'POST':
        form = HodnotenieForm(request.POST)
        if form.is_valid():
            hodnotenie = form.save(commit=False)
            hodnotenie.udalost = udalost  
            hodnotenie.profil = profil     
            hodnotenie.save()
            
            messages.success(request, "Hodnotenie úspešne pridané!")
            return redirect('udalost_archiv')
    else:
        form = HodnotenieForm()

    context = {
        'form': form,
        'udalost': udalost,
        'profil': profil,
    }
    return render(request, 'core/hodnotenie_create.html', context)


def tim_list_view(request):
    """Zobrazí zoznam všetkých tímov."""
    vsetky_timy = Tim.objects.all()
    context = {'timy': vsetky_timy}
    return render(request, 'core/tim_list.html', context)


def tim_create_view(request):
    """Vytvorenie nového tímu."""
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
    """Pripojenie sa k tímu."""
    if not request.user.is_authenticated: return redirect('login')
    tim = get_object_or_404(Tim, id=tim_id)
    profil = request.user.profil
    if Tim.objects.filter(clenovia=profil).exists(): return redirect('tim_list') 
    if tim.clenovia.count() >= MAX_TEAM_SIZE: return redirect('tim_list') 
    tim.clenovia.add(profil)
    return redirect('tim_list')


def rebricky_view(request):
    """Zobrazí tri rebríčky (Denný, Týždenný, Mesačný) podľa aktivity."""
    now = timezone.now()

    denny_limit = now - timedelta(days=1)
    top_denne = Profil.objects.filter(prihlasene_udalosti__datum_konania__gte=denny_limit)\
        .annotate(score=Count('prihlasene_udalosti'))\
        .order_by('-score')[:5]

    tyzdenny_limit = now - timedelta(days=7)
    top_tyzdenne = Profil.objects.filter(prihlasene_udalosti__datum_konania__gte=tyzdenny_limit)\
        .annotate(score=Count('prihlasene_udalosti'))\
        .order_by('-score')[:5]

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
    """Zobrazí len relevantné notifikácie a vynuluje počítadlo zvončeka."""
    if not request.user.is_authenticated: return redirect('login')
    
    profil = request.user.profil
    now = timezone.now()
    limit = now + timedelta(days=1) 

    moje_urgentne = Udalost.objects.filter(
        ucastnici=profil,           
        datum_konania__gt=now,
        datum_konania__lte=limit
    ).order_by('datum_konania')

    ziadosti = FriendRequest.objects.filter(pre_koho=profil)

    total_count = moje_urgentne.count() + ziadosti.count()
    request.session['videny_pocet_notifikacii'] = total_count

    context = {
        'moje_urgentne': moje_urgentne,
        'ziadosti': ziadosti,
    }
    return render(request, 'core/oznamenie_list.html', context)