from django.contrib import admin
from .models import (
    Profil, Hra, Udalost, Tim, Oznamenie, Priatelstvo, 
    Odoslanie, Hodnotenie, FriendRequest, Rola
)


admin.site.register(Profil)
admin.site.register(Hra)
admin.site.register(Udalost)
admin.site.register(Tim)
admin.site.register(Oznamenie)
admin.site.register(Priatelstvo)
admin.site.register(Odoslanie)
admin.site.register(Hodnotenie)
admin.site.register(FriendRequest)
admin.site.register(Rola)