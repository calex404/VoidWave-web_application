# core/context_processors.py

from .models import Odoslanie, Priatelstvo
from django.db.models import Q # Pre hľadanie priateľstiev

def unread_notification_count(request):
    """Pridá celkový počet neprečítaných oznámení a čakajúcich žiadostí do kontextu."""
    
    if request.user.is_authenticated and request.user.profil:
        profil = request.user.profil
        
        # 1. Neprečítané oznámenia (kde stav je 'neprecitane')
        unread_messages = Odoslanie.objects.filter(
            prijemca=profil, stav='neprecitane'
        ).count()
        
        # 2. Čakajúce žiadosti o priateľstvo (stav 'pending')
        pending_requests = Priatelstvo.objects.filter(
            profil2=profil, stav='pending'
        ).count()
        
        total_unread = unread_messages + pending_requests
        
        return {'total_unread_count': total_unread}
    
    return {} # Pre odhlásených používateľov vráti prázdny slovník