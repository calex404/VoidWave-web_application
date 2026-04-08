from datetime import timedelta, datetime
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


def home_view(request):
    
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

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            Profil.objects.get_or_create(user=user, defaults={'nickname': user.username})
            
            messages.success(request, "✅ Registrácia bola úspešná! Teraz sa môžeš prihlásiť.")
            
            return redirect('home') 
            
    else:
        form = CustomUserCreationForm()
        
    context = { 'form': form, 'nadpis': 'Registrácia nového používateľa' }
    return render(request, 'registration/register.html', context)


def dashboard_view(request):

    if not request.user.is_authenticated:
        return redirect('login')
    
    profil = request.user.profil

    context = {
        'profil': profil,
    }
    return render(request, 'core/dashboard.html', context)


def profil_list_view(request):
    hladame_priatelov = 'hladat' in request.path

    profily_qs = Profil.objects.all()
    if hladame_priatelov:
        profily_qs = profily_qs.exclude(user=request.user)

    profily = list(profily_qs)

    if request.user.is_authenticated:
        try:
            moj_profil = request.user.profil
        except AttributeError:
            moj_profil = request.user.profile

        for p in profily:
            p.ziadost_odoslana = FriendRequest.objects.filter(
                od_koho=moj_profil,
                pre_koho=p
            ).exists()

            p.sme_kamosi = False

    context = {
        'profily': profily,
        'hladame_priatelov': hladame_priatelov
    }
    return render(request, 'core/profil_list.html', context)


def find_priatelov_view(request):
    hladame_priatelov = True
    try:
        moj_profil = request.user.profil
    except AttributeError:
        moj_profil = request.user.profile

    # 1. NÁJDEME VŠETKY ID, KTORÉ CHCEME SCHOVAŤ (lotricek a spol.)
    # Hľadáme všetky žiadosti, kde figuruješ ty
    moje_vztahy = FriendRequest.objects.filter(
        Q(od_koho=moj_profil) | Q(pre_koho=moj_profil)
    )

    vylucit_ids = set()
    for vztah in moje_vztahy:
        vylucit_ids.add(vztah.od_koho.id)
        vylucit_ids.add(vztah.pre_koho.id)

    # 2. FILTER: Ukáž mi len tých, čo nie sú JA a nie sú vo "vylucit_ids"
    # Týmto lotricek definitívne zmizne, ak s ním existuje záznam.
    profily = Profil.objects.all().exclude(
        user=request.user
    ).exclude(
        id__in=list(vylucit_ids)
    )

    context = {
        'profily': profily,
        'hladame_priatelov': hladame_priatelov  
    }
    
    # FIX CESTY: 'core/profil_list.html'
    return render(request, 'core/profil_list.html', context)


def profil_detail_view(request, profil_id):
 
    profil = get_object_or_404(Profil, id=profil_id)
    
    priatelia = Priatelstvo.objects.filter(
        Q(profil1=profil) | Q(profil2=profil),
        stav='accepted'
    )

    context = {
        'profil': profil,
        'priatelia': priatelia,
    }
    return render(request, 'core/profil_detail.html', context)


def profil_edit_view(request):
    
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
    if request.method == "POST" and request.user.is_authenticated:
        od_koho = request.user.profil
        pre_koho = get_object_or_404(Profil, id=profil_id)

        if od_koho == pre_koho:
            return redirect(request.META.get("HTTP_REFERER", "profil_list"))

        fr, created = FriendRequest.objects.get_or_create(
            od_koho=od_koho,
            pre_koho=pre_koho
        )

        p1, p2 = sorted([od_koho, pre_koho], key=lambda x: x.id)

        Priatelstvo.objects.get_or_create(
            profil1=p1,
            profil2=p2,
            defaults={"stav": "pending"}
        )

        messages.success(request, "Žiadosť bola odoslaná")

    return redirect(request.META.get("HTTP_REFERER", "profil_list"))



def accept_friend_request(request, request_id):
    if not request.user.is_authenticated:
        return redirect('login')

    ziadost = get_object_or_404(FriendRequest, id=request_id)

    if ziadost.pre_koho == request.user.profil:
        p1, p2 = sorted(
            [ziadost.od_koho, ziadost.pre_koho],
            key=lambda x: x.id
        )

        Priatelstvo.objects.filter(
            profil1=p1,
            profil2=p2,
            stav='pending'
        ).update(stav='accepted')

        ziadost.delete()

        messages.success(
            request,
            f"Teraz si priateľ s {ziadost.od_koho.nickname}!"
        )

    return redirect('oznamenie_list')


def reject_friend_request(request, request_id):

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

    vsetky_hry = Hra.objects.all()
    context = { 'hry': vsetky_hry, 'nadpis': 'Katalóg hier', }
    return render(request, 'core/hra_list.html', context)


def hra_detail_view(request, hra_id):

    hra = get_object_or_404(Hra, id=hra_id)
    context = {'hra': hra}
    return render(request, 'core/hra_detail.html', context)


def udalost_list_view(request):

    now = timezone.now()
    udalosti = Udalost.objects.filter(datum_konania__gte=now).order_by('datum_konania')
    
    return render(request, 'core/udalost_list.html', {'udalosti': udalosti})


def udalost_archiv_view(request):
    
    now = timezone.now() 
    archiv_udalosti = Udalost.objects.filter(datum_konania__lt=now).order_by('-datum_konania')

    udalosti_s_hodnotenim = []
    current_profil = request.user.profil if request.user.is_authenticated else None
    
    for udalost in archiv_udalosti:
        vsetky_hodnotenia = Hodnotenie.objects.filter(udalost=udalost).order_by('-datum_hodnotenia') 
        
        if vsetky_hodnotenia.exists():
            priemer = vsetky_hodnotenia.aggregate(Avg('hodnotenie'))['hodnotenie__avg']
            priemer_hodnotou = round(priemer, 2)
        else:
            priemer_hodnotou = None
        
        uz_som_hodnotil = False
        if current_profil:

             uz_som_hodnotil = Hodnotenie.objects.filter(profil=current_profil, udalost=udalost).exists()
        
        udalosti_s_hodnotenim.append({
            'udalost': udalost,
            'uz_som_hodnotil': uz_som_hodnotil, 
            'priemer': priemer_hodnotou, 
            'vsetky_hodnotenia': vsetky_hodnotenia,
        })

    context = {'udalosti': udalosti_s_hodnotenim}
    return render(request, 'core/udalost_archive.html', context)


def udalost_create_view(request):

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


def hodnotenie_create_view(request, udalost_id):
    
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

    vsetky_timy = Tim.objects.all()
    context = {'timy': vsetky_timy}
    return render(request, 'core/tim_list.html', context)


def tim_create_view(request):

    if not request.user.is_authenticated: return redirect('login')

    if not request.user.is_superuser:
        if Tim.objects.filter(clenovia=request.user.profil).exists():
            messages.warning(request, "Nemôžeš založiť nový tím, pretože už si členom iného.")
            return redirect('tim_list') 

    if request.method == 'POST':
        form = TimForm(request.POST)
        if form.is_valid():
            novy_tim = form.save()
            novy_tim.clenovia.add(request.user.profil)
            novy_tim.save()
            messages.success(request, "Tím bol úspešne vytvorený!")
            return redirect('tim_list')
    else:
        form = TimForm()

    context = { 'form': form, 'nadpis': 'Založiť nový tím' }
    return render(request, 'core/tim_form.html', context)


def tim_join_view(request, tim_id):

    MAX_TEAM_SIZE = 5

    if not request.user.is_authenticated: return redirect('login')
    tim = get_object_or_404(Tim, id=tim_id)
    profil = request.user.profil
    
    if not request.user.is_superuser and Tim.objects.filter(clenovia=profil).exists():
        messages.warning(request, "Nemôžeš sa pridať do iného tímu, kým si členom svojho súčasného.")
        return redirect('tim_list') 
        
    if tim.clenovia.count() >= MAX_TEAM_SIZE:
        messages.error(request, "Tento tím je už plný.")
        return redirect('tim_list') 
    
    tim.clenovia.add(profil)
    messages.success(request, f"Vitaj v tíme {tim.nazov}!")
    return redirect('tim_list')


def tim_leave_view(request, tim_id):

    if not request.user.is_authenticated: return redirect('login')
    tim = get_object_or_404(Tim, id=tim_id)
    profil = request.user.profil
    
    if tim.clenovia.filter(id=profil.id).exists():
        tim.clenovia.remove(profil)
        messages.success(request, f"Opustil/a si tím {tim.nazov}.")
    
    return redirect('tim_list')


def rebricky_view(request):

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