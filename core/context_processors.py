from datetime import timedelta
from django.utils import timezone
from .models import Udalost, FriendRequest, Profil 


def notifikacie_processor(request):
    """
    Vypočítava počet NOVÝCH (nezhliadnutých) notifikácií pre červený odznak.
    
    Obsah badge count: Žiadosti o priateľstvo + Urgentné udalosti (do 24h).
    """
    
    realny_pocet_aktualny = 0
    
    if request.user.is_authenticated:
        try:
            profil = getattr(request.user, 'profil', None)
            
            if profil:
                ziadosti_count = FriendRequest.objects.filter(pre_koho=profil).count()
                
                now = timezone.now()
                limit_den = now + timedelta(days=1)
                
                urgentne_count = Udalost.objects.filter(
                    ucastnici=profil,       
                    datum_konania__gt=now, 
                    datum_konania__lte=limit_den
                ).count()
                
                realny_pocet_aktualny = ziadosti_count + urgentne_count
            
        except Exception:
            realny_pocet_aktualny = 0


    videny_pocet = request.session.get('videny_pocet_notifikacii', 0)
    
    badge_cislo = realny_pocet_aktualny - videny_pocet
    
    if badge_cislo < 0:
        badge_cislo = 0

    return {'badge_cislo': badge_cislo}