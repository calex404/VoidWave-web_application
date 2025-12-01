from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Profil, Udalost, Hra, Hodnotenie, Odoslanie, Priatelstvo, Umiestnenie
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Kompletná simulácia: Vymaže staré dáta a vygeneruje čisté názvy (len [SKRATKA] #Cislo).'

    def handle(self, *args, **kwargs):
        
        self.stdout.write(self.style.WARNING('--- ČISTÍM DATABÁZU ---'))
        
        Hodnotenie.objects.all().delete()
        Odoslanie.objects.all().delete()
        Priatelstvo.objects.all().delete()
        Umiestnenie.objects.all().delete()
        Udalost.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('Databáza vyčistená.'))

        profily = list(Profil.objects.all())
        hry = list(Hra.objects.all())

        if not profily or not hry:
            self.stdout.write(self.style.ERROR('Chyba: V databáze chýbajú profily alebo hry!'))
            return

        now = timezone.now()
        
        # ---------------------------------------------------------
        # 2. GENERÁCIA MINULOSTI (Archív)
        # ---------------------------------------------------------
        self.stdout.write('\n--- GENERUJEM MINULOSŤ (Archív) ---')
        for i in range(5): 
            dni_dozadu = random.randint(1, 30)
            den_udalosti = now - timedelta(days=dni_dozadu)
            
            # Čas
            final_datum = den_udalosti.replace(hour=random.randint(10, 23), minute=0, second=0)
            if final_datum > now: final_datum -= timedelta(days=1)

            self.vytvor_udalost(final_datum, hry, profily)

        # ---------------------------------------------------------
        # 3. GENERÁCIA BUDÚCNOSTI (Aktuálne)
        # ---------------------------------------------------------
        self.stdout.write('\n--- GENERUJEM BUDÚCNOSŤ (Aktuálne) ---')
        for i in range(5):
            dni_dopredu = random.randint(1, 30)
            den_udalosti = now + timedelta(days=dni_dopredu)
            
            # Čas
            final_datum = den_udalosti.replace(hour=random.randint(10, 23), minute=0, second=0)

            self.vytvor_udalost(final_datum, hry, profily)

        self.stdout.write(self.style.SUCCESS('\n-------------------------------------'))
        self.stdout.write(self.style.SUCCESS('HOTOVO! Názvy sú teraz len [SKRATKA] #Číslo.'))


    def vytvor_udalost(self, datum, hry, profily):
        """Pomocná funkcia na vytvorenie jednej udalosti."""
        hra = random.choice(hry)
        organizator = random.choice(profily)
        typ_eventu = random.choice(['match', 'tournament', 'raid', 'duel'])
        male_cislo = random.randint(1, 99)
        
        # 💥 FINÁLNY ČISTÝ NÁZOV: [SKRATKA] #Číslo 💥
        # Napr. [FAC] #42
        cisty_nazov = f"[{hra.nazov[:3].upper()}] #{male_cislo}"

        nova_udalost = Udalost.objects.create(
            nazov=cisty_nazov,
            popis="Automaticky vygenerovaná udalosť.",
            datum_konania=datum,
            typ=typ_eventu, 
            organizator=organizator,
            hra=hra
        )

        # Pridanie účastníkov
        pocet_ludi = random.randint(2, min(5, len(profily)))
        ucastnici = random.sample(profily, k=pocet_ludi)
        for p in ucastnici:
            nova_udalost.ucastnici.add(p)

        self.stdout.write(f" -> Vytvorené: {nova_udalost.nazov} ({datum.strftime('%d.%m %H:%M')})")