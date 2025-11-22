from django.shortcuts import render
from .models import Profil 
from datetime import datetime

def profil_list_view(request):
   
    vsetky_profily = Profil.objects.all()
    context = {
        'profily': vsetky_profily,
        'datum_a_cas': datetime.now()
    }
    
    return render(request, 'core/profil_list.html', context)
