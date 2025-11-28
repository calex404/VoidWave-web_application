import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Profil, Udalost, Hra

class Command(BaseCommand):
    help = 'Smart simulácia 3.0: Pekné časy, rozumné hodiny a lepší rozptyl'

    def add_arguments(self, parser):
        parser.add_argument('typ', type=str, help='Použi: minulost alebo buducnost')

    def handle(self, *args, **kwargs):
        typ_simulacie = kwargs['typ']
        profily = list(Profil.objects.all())
        hry = list(Hra.objects.all())

        if not profily or not hry:
            self.stdout.write(self.style.ERROR('Chýbajú profily alebo hry v DB!'))
            return

        now = timezone.now()
        pocet_akcii = 3  # Znížený počet, aby sme nespamovali

        self.stdout.write(f"--- Generujem {typ_simulacie.upper()} (Interval 10:00 - 23:55) ---")

        for i in range(pocet_akcii):
            # 1. GENERÁCIA DÁTUMU (Rozptyl)
            if typ_simulacie == 'minulost':
                # Vyberieme náhodný deň za posledných 30 dní
                # 0 = dnes, 1 = včera ... 30 = pred mesiacom
                dni_dozadu = random.randint(0, 30)
                den_udalosti = now - timedelta(days=dni_dozadu)
                prefix = "Odohraný Zápas"
            
            elif typ_simulacie == 'buducnost':
                # Vyberieme náhodný deň v najbližších 30 dňoch
                dni_dopredu = random.randint(1, 30)
                den_udalosti = now + timedelta(days=dni_dopredu)
                prefix = "Veľký Turnaj"
            
            else:
                self.stdout.write(self.style.ERROR("Neznámy typ. Použi: 'minulost' alebo 'buducnost'"))
                return

            # 2. GENERÁCIA ČASU (Estetika)
            # Hodina: 10:00 až 23:00
            nahodna_hodina = random.randint(10, 23)
            # Minúta: Len násobky 5 (0, 5, 10, ... 55)
            nahodna_minuta = random.choice(range(0, 60, 5))

            # Spojíme deň a čas
            final_datum = den_udalosti.replace(hour=nahodna_hodina, minute=nahodna_minuta, second=0, microsecond=0)

            # Poistka pre minulosť: Ak sme vybrali "dnes", ale čas je v budúcnosti (napr. je 12:00 a vybralo 18:00),
            # posunieme to o deň dozadu, aby to bolo naozaj v minulosti.
            if typ_simulacie == 'minulost' and final_datum > now:
                final_datum -= timedelta(days=1)

            # 3. ZVYŠOK (Hra, Organizátor, Účastníci)
            hra = random.choice(hry)
            organizator = random.choice(profily)
            typ_eventu = random.choice(['match', 'tournament', 'raid', 'duel'])

            # Vytvorenie udalosti
            nova_udalost = Udalost.objects.create(
                nazov=f"{prefix} [{hra.nazov[:3].upper()}] #{random.randint(100, 999)}",
                popis="Automaticky vygenerovaná udalosť (Simulácia 3.0)",
                datum_konania=final_datum,
                typ=typ_eventu,
                organizator=organizator,
                hra=hra
            )

            # Pridanie účastníkov
            počet_ludi = random.randint(2, min(5, len(profily)))
            ucastnici = random.sample(profily, k=počet_ludi)
            for p in ucastnici:
                nova_udalost.ucastnici.add(p)

            # Výpis do konzoly
            self.stdout.write(f" -> {nova_udalost.nazov} | {final_datum.strftime('%d.%m %H:%M')}")

        self.stdout.write(self.style.SUCCESS('Hotovo.'))

    # python3 manage.py simulation minulost