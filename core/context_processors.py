from django.utils import timezone
from datetime import timedelta
from .models import Udalost, FriendRequest

def notifikacie_processor(request):
    """
    Počíta LEN nové (nevidené) notifikácie.
    """
    realny_pocet = 0
    
    if request.user.is_authenticated:
        try:
            profil = getattr(request.user, 'profil', None)
            if profil:
                # 1. Žiadosti o priateľstvo
                ziadosti = FriendRequest.objects.filter(pre_koho=profil).count()
                
                # 2. Udalosti (LEN tie, kde som prihlásený a sú do 24h)
                now = timezone.now()
                limit = now + timedelta(days=1)
                
                urgentne = Udalost.objects.filter(
                    ucastnici=profil,       # <--- Len moje
                    datum_konania__gt=now, 
                    datum_konania__lte=limit
                ).count()
                
                realny_pocet = ziadosti + urgentne
                
        except Exception:
            realny_pocet = 0

    # LOGIKA PRE ZMIZNUTIE ČÍSLA:
    # Načítame zo session, koľko sme videli naposledy
    videny_pocet = request.session.get('videny_pocet_notifikacii', 0)
    
    # Zobrazíme len rozdiel (ak pribudlo niečo nové)
    badge_cislo = realny_pocet - videny_pocet
    
    # Ak je výsledok záporný (napr. si niečo vymazala), ukážeme 0
    if badge_cislo < 0:
        badge_cislo = 0

    return {'badge_cislo': badge_cislo}