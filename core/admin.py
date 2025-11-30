from django.contrib import admin
from .models import (
    Rola, Profil, Priatelstvo, Hra, Rebricek, Tim, Umiestnenie, Udalost, Hodnotenie, Oznamenie, Odoslanie
)

admin.site.register(Rola)
admin.site.register(Profil)
admin.site.register(Priatelstvo)
admin.site.register(Hra)
admin.site.register(Rebricek)
admin.site.register(Tim)
admin.site.register(Umiestnenie)
admin.site.register(Udalost)
admin.site.register(Hodnotenie)
admin.site.register(Oznamenie)
admin.site.register(Odoslanie)