import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Profil, Udalost, Hra

class Command(BaseCommand):
    help = 'Smart simulácia: generuje minulosť (pre rebríčky) alebo budúcnosť (pre plán)'

    def add_arguments(self, parser):
        # Argument bude: 'minulost' alebo 'buducnost'
        parser.add_argument('typ', type=str, help='Použi: minulost alebo buducnost')

    def handle(self, *args, **kwargs):
        typ_simulacie = kwargs['typ']
        profily = list(Profil.objects.all())
        hry = list(Hra.objects.all())

        if not profily or not hry:
            self.stdout.write(self.style.ERROR('Chýbajú profily alebo hry v DB!'))
            return

        now = timezone.now()
        
        # KONFIGURÁCIA PODĽA TYPU
        if typ_simulacie == 'minulost':
            self.stdout.write("--- Generujem ARCHÍVNE dáta (pre Rebríčky) ---")
            pocet_akcii = 5
            # Časový rozsah: od včera do pred hodinou (aby to bolo v rebríčku Denný)
            start_window = now - timedelta(hours=20)
            end_window = now - timedelta(hours=1)
            prefix = "Odohraný Zápas"

        elif typ_simulacie == 'buducnost':
            self.stdout.write("--- Generujem BUDÚCE dáta (pre Plánovanie) ---")
            pocet_akcii = 3
            # Časový rozsah: od zajtra do +30 dní
            start_window = now + timedelta(days=1)
            end_window = now + timedelta(days=30)
            prefix = "Veľký Turnaj"
        
        else:
            self.stdout.write(self.style.ERROR("Neznámy typ. Použi: 'minulost' alebo 'buducnost'"))
            return

        # GENERÁTOR
        for i in range(pocet_akcii):
            # 1. Náhodný čas v rozsahu (aby sa neprekrývali na sekundu presne)
            # Vypočítame rozdiel v sekundách a vyberieme náhodný posun
            time_diff = (end_window - start_window).total_seconds()
            random_seconds = random.randint(0, int(time_diff))
            final_datum = start_window + timedelta(seconds=random_seconds)

            # 2. Náhodná hra a organizátor
            hra = random.choice(hry)
            organizator = random.choice(profily)
            typ_eventu = random.choice(['match', 'tournament', 'raid', 'duel'])

            # 3. Vytvorenie udalosti
            nova_udalost = Udalost.objects.create(
                nazov=f"{prefix} [{hra.nazov[:3].upper()}] #{random.randint(10, 99)}",
                popis="Automaticky vygenerovaná udalosť pre demonštráciu.",
                datum_konania=final_datum,
                typ=typ_eventu,
                organizator=organizator,
                hra=hra
            )

            # 4. Pridanie účastníkov (bez hodnotení, tie robíš ručne)
            # Vyberieme náhodnú vzorku (2 až 6 ľudí)
            počet_ludi = random.randint(2, min(6, len(profily)))
            ucastnici = random.sample(profily, k=počet_ludi)
            
            for p in ucastnici:
                nova_udalost.ucastnici.add(p)

            self.stdout.write(f" -> {nova_udalost.nazov} | {final_datum.strftime('%d.%m %H:%M')} | Hra: {hra.nazov}")

        self.stdout.write(self.style.SUCCESS('Hotovo.'))