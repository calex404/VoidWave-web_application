from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError 
from django.db.models import Q 


User = get_user_model()


class Rola(models.Model):
    """Definuje roly používateľov (napr. Organizátor, Admin)."""
    nazov_role = models.CharField(max_length=64, unique=True)
    
    def __str__(self):
        return self.nazov_role


class Profil(models.Model):
    """Rozšírenie Django User modelu o herné a komunitné informácie."""
    nickname = models.CharField(max_length=64, unique=True) 
    bio = models.TextField(null=True, blank=True) 
    uroven = models.IntegerField(default=1)
    datum_registracie = models.DateField(auto_now_add=True) 
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    rola = models.ForeignKey(Rola, on_delete=models.SET_NULL, null=True, blank=True) 
    
    def __str__(self):
        return self.nickname


class FriendRequest(models.Model):
    """Model pre dočasné uloženie PENDING žiadostí (pre notifikačný zvonček)."""
    od_koho = models.ForeignKey(Profil, related_name='odoslane_ziadosti', on_delete=models.CASCADE)
    pre_koho = models.ForeignKey(Profil, related_name='prijate_ziadosti', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Žiadosť: {self.od_koho} -> {self.pre_koho}"


class Priatelstvo(models.Model):
    """
    Model pre existujúce priateľstvá s ochranou proti duplicitám.
    Vždy uloží profil s menším ID ako profil1.
    """
    profil1 = models.ForeignKey(Profil, related_name='priatelstva_1', on_delete=models.CASCADE)
    profil2 = models.ForeignKey(Profil, related_name='priatelstva_2', on_delete=models.CASCADE)
    stav = models.CharField(max_length=20, choices=[
        ('pending', 'Čakajúce'), ('accepted', 'Prijaté'), ('blocked', 'Blokované')
    ], default='pending')
    datum_vytvorenia = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('profil1', 'profil2') 

    def save(self, *args, **kwargs):
        if self.profil1_id > self.profil2_id:
            self.profil1, self.profil2 = self.profil2, self.profil1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.profil1.nickname} - {self.profil2.nickname} ({self.stav})"


class Hra(models.Model):
    """Katalóg hier."""
    nazov = models.CharField(max_length=64, unique=True) 
    
    ZANER_CHOICES = [
        ('fps', 'FPS'), ('tps', 'TPS'), ('battleroyal', 'Battle Royale'),
        ('moba', 'MOBA'), ('rpg', 'RPG'), ('mmorpg', 'MMORPG'),
        ('survival', 'Survival'), ('openworld', 'Open World'),
        ('fighting', 'Fighting'), ('sports', 'Sports'), ('racing', 'Racing'),
        ('strategy', 'Strategy'), ('adventure', 'Adventure'), 
        ('partygames', 'Party Games'), ('card', 'Card'), ('simulator', 'Simulator'),  
    ]

    zaner = models.CharField(max_length=64, choices=ZANER_CHOICES) 
    bio = models.TextField(null=True, blank=True) 
    
    def __str__(self):
        return self.nazov


class Tim(models.Model):
    """Základný model pre herné tímy."""
    nazov = models.CharField(max_length=64, unique=True) 
    bio = models.TextField(null=True, blank=True) 
    uroven = models.IntegerField(default=1) 
    
    clenovia = models.ManyToManyField(Profil, related_name='timy_clenom_je')
    
    def __str__(self):
        return self.nazov


class Udalost(models.Model):
    """Hlavný model pre herné akcie, turnaje a pod."""
    nazov = models.CharField(max_length=64) 
    datum_konania = models.DateTimeField() 
    
    popis = models.TextField(null=True, blank=True)
    
    ucastnici = models.ManyToManyField('Profil', related_name='prihlasene_udalosti', blank=True)
    
    TYP_CHOICES = [
        ('mission', 'Mission'), ('quest', 'Quest'), ('challenge', 'Challenge'),
        ('event', 'Event'), ('match', 'Match') , ('battle', 'Battle'),
        ('duel', 'Duel'), ('raid', 'Raid'), ('tournament', 'Tournament'), 
        ('dungeon', 'Dungeon'),
    ]

    typ = models.CharField(max_length=64, choices=TYP_CHOICES) 
    organizator = models.ForeignKey(Profil, on_delete=models.SET_NULL, null=True, related_name='udalosti_organizovane')
    hra = models.ForeignKey(Hra, on_delete=models.CASCADE) 
    
    def __str__(self):
        return f"{self.nazov} ({self.typ})"


class Hodnotenie(models.Model):
    """Hodnotenie Udalosti alebo Hry."""
    hodnotenie = models.IntegerField() 
    datum_hodnotenia = models.DateField(auto_now_add=True) 
    
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE) 
    hra = models.ForeignKey(Hra, on_delete=models.SET_NULL, null=True, blank=True)
    udalost = models.ForeignKey(Udalost, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(hra__isnull=False, udalost__isnull=True) | models.Q(hra__isnull=True, udalost__isnull=False),
                name='jedinecny_objekt_hodnotenia'
            )
        ]
        
    def __str__(self):
        objekt_nazov = self.hra.nazov if self.hra else self.udalost.nazov
        return f"Hodnotenie {self.hodnotenie}/10 pre {objekt_nazov}"


class Rebricek(models.Model):
    """Model pre dynamicky počítané rebríčky (historické snapshoty)."""
    TYP_CHOICES = [
        ('denny', 'Denný'), ('tyzdenny', 'Týždenný'), ('mesacny', 'Mesačný'), 
    ]
    typ = models.CharField(max_length=64, choices=TYP_CHOICES) 
    datum_aktualizacie = models.DateField() 
    
    def __str__(self):
        return f"Rebríček: {self.typ}"


class Umiestnenie(models.Model):
    """Umiestnenie tímu v danom rebríčku."""
    tim = models.ForeignKey(Tim, on_delete=models.CASCADE) 
    rebricek = models.ForeignKey(Rebricek, on_delete=models.CASCADE)
    
    pozicia = models.IntegerField() 
    body = models.IntegerField() 
    
    class Meta:
        unique_together = ('tim', 'rebricek')
        
    def __str__(self):
        return f"{self.tim.nazov} v {self.rebricek.typ} na {self.pozicia}. mieste"


class Oznamenie(models.Model):
    """Obsah notifikácie (text správy)."""
    nazov = models.CharField(max_length=255, default='Systémová správa') 
    TYP_CHOICES = [('pozvanka', 'Pozvánka'), ('upozornenie', 'Upozornenie'), ('sprava', 'Správa')]
    typ = models.CharField(max_length=15, choices=TYP_CHOICES, default='sprava') 
    obsah = models.TextField()
    datum_vytvorenia = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.nazov} ({self.typ})"

class Odoslanie(models.Model):
    """Záznam o odoslanej notifikácii konkrétnemu príjemcovi."""
    oznamenie = models.ForeignKey(Oznamenie, on_delete=models.CASCADE)
    prijemca = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='prijate_oznamenia')
    
    datum_odoslania = models.DateTimeField(auto_now_add=True) 
    datum_precitania = models.DateTimeField(null=True, blank=True)
    
    STAV_CHOICES = [('neprecitane', 'Neprečítané'), ('precitane', 'Prečítané')]
    stav = models.CharField(max_length=64, choices=STAV_CHOICES, default='neprecitane')

    def __str__(self):
        return f"Oznámenie pre {self.prijemca.nickname} - {self.stav}"