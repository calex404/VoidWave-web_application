import random
from django.core.management.base import BaseCommand
from core.models import Profil, Udalost

class Command(BaseCommand):
    help = 'Simuluje aktivitu uzivatelov (denne, tyzdenne, mesacne)'

    def add_arguments(self, parser):
        # Prijímame argument: denne / tyzdenne / mesacne
        parser.add_argument('obdobie', type=str, help='Typ aktualizacie: denne, tyzdenne, mesacne')

    def handle(self, *args, **kwargs):
        obdobie = kwargs['obdobie']
        profily = Profil.objects.all()
        udalosti = Udalost.objects.all()

        if not profily.exists():
            self.stdout.write(self.style.ERROR('Ziadne profily v DB! Vytvor najprv uzivatelov.'))
            return

        self.stdout.write(f"--- Spúšťam simuláciu: {obdobie.upper()} ---")

        # NASTAVENIE INTENZITY ZMIEN
        if obdobie == 'denne':
            sanca_level = 0.3    # 30% šanca na level up
            max_level_up = 1     
            sanca_ucast = 0.2    # 20% šanca na účasť
        elif obdobie == 'tyzdenne':
            sanca_level = 0.6
            max_level_up = 3
            sanca_ucast = 0.5
        elif obdobie == 'mesacne':
            sanca_level = 0.9
            max_level_up = 5
            sanca_ucast = 0.8
        else:
            self.stdout.write(self.style.ERROR('Nezname obdobie. Pouzi: denne, tyzdenne, mesacne'))
            return

        # 1. UPDATE LEVELOV (Rebríček Úrovne)
        count_level = 0
        for p in profily:
            if random.random() < sanca_level:
                narast = random.randint(1, max_level_up)
                p.uroven += narast
                p.save()
                count_level += 1
                # Odkomentuj, ak chceš vidieť každé meno v konzole:
                # self.stdout.write(f" -> {p.nickname} +{narast} lvl")

        self.stdout.write(self.style.SUCCESS(f"Level up dostalo {count_level} používateľov."))

        # 2. UPDATE ÚČASTI (Rebríček Aktivity)
        count_ucast = 0
        if udalosti.exists():
            for p in profily:
                if random.random() < sanca_ucast:
                    # Vyberieme náhodnú udalosť
                    nahodna_udalost = random.choice(udalosti)
                    
                    # Ak tam ešte nie je, pridáme ho
                    if not nahodna_udalost.ucastnici.filter(id=p.id).exists():
                        nahodna_udalost.ucastnici.add(p)
                        count_ucast += 1

        self.stdout.write(self.style.SUCCESS(f"Pridaných {count_ucast} nových účastí na udalosti."))
        self.stdout.write(self.style.SUCCESS(f'--- HOTOVO ({obdobie}) ---'))