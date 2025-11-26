from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

class Rola(models.Model):
    
    nazov_role = models.CharField(max_length = 64, unique = True)
    
    def __str__(self):
        return self.nazov_role

class Profil(models.Model):

    nickname = models.CharField(max_length=64, unique=True) 
    bio = models.TextField(null=True, blank=True) 
    uroven = models.IntegerField(default=1)
    datum_registracie = models.DateField(auto_now_add=True) 
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
 
    # vztah N:1
    rola = models.ForeignKey(Rola, on_delete=models.SET_NULL, null=True) 
   
    def __str__(self):
        return self.nickname
    
class Priatelstvo(models.Model):

    profil1 = models.ForeignKey(
        Profil, 
        on_delete=models.CASCADE, # kaskadove mazanie
        related_name='ziadost_odoslana' 
    )
    
    profil2 = models.ForeignKey(
        Profil, 
        on_delete=models.CASCADE, 
        related_name='ziadost_prijata' 
    )

    STAV_CHOICES = [
        ('pending', 'Pending'), 
        ('accepted', 'Accepted'), 
        ('blocked', 'Blocked'), 
    ]

    stav = models.CharField(max_length=10, choices=STAV_CHOICES, default='pending') 
    datum = models.DateField(auto_now_add=True) 

    def __str__(self):
        return f"{self.profil1.nickname} - {self.profil2.nickname} ({self.stav})"

    # zabezpecenie aby bolo priatelstvo jedinecne
    class Meta:
        unique_together = ('profil1', 'profil2')

class Hra(models.Model):

    nazov = models.CharField(max_length=64, unique=True) 
    
    ZANER_CHOICES = [
        ('fps', 'FPS'), 
        ('tps', 'TPS'), 
        ('battleroyal', 'Battle Royale'),
        ('moba', 'MOBA'),
        ('rpg', 'RPG'), 
        ('mmorpg', 'MMORPG'),
        ('survival', 'Survival'), 
        ('openworld', 'Open World'),
        ('fighting', 'Fighting'),  
        ('sports', 'Sports'), 
        ('racing', 'Racing'),
        ('strategy', 'Strategy'),
        ('adventure', 'Adventure'), 
        ('partygames', 'RPG'),   
        ('card', 'Card'),
        ('simulator', 'Simulator'),  
    ]

    zaner = models.CharField(max_length=64, choices=ZANER_CHOICES) 
    bio = models.TextField(null=True, blank=True) 
    
    def __str__(self):
        return self.nazov

class Rebricek(models.Model):

    TYP_CHOICES = [
        ('tyzdenny', 'Týždenný'), 
        ('mesacny', 'Mesačný'), 
        ('rocny', 'Ročný'),
    ]

    typ = models.CharField(max_length=64, choices=TYP_CHOICES) 
    datum_aktualizacie = models.DateField() 
    
    def __str__(self):
        return f"Rebríček: {self.typ}"

class Tim(models.Model):
 
    nazov = models.CharField(max_length=64, unique=True) 
    bio = models.TextField(null=True, blank=True) 
    uroven = models.IntegerField(default=1) 
    
    # vztah M:N 
    clenovia = models.ManyToManyField(Profil, related_name='timy_clenom_je')
    
    def __str__(self):
        return self.nazov

# spojovacia entita M:N 
class Umiestnenie(models.Model):
    
    tim = models.ForeignKey(Tim, on_delete=models.CASCADE) 
    rebricek = models.ForeignKey(Rebricek, on_delete=models.CASCADE)
    
    pozicia = models.IntegerField() 
    body = models.IntegerField() 
    
    class Meta:
        # zabezpecenie aby bol jeden tim v danom rebricku iba raz 
        unique_together = ('tim', 'rebricek')
        
    def __str__(self):
        return f"{self.tim.nazov} v {self.rebricek.typ} na {self.pozicia}. mieste"

class Udalost(models.Model):
    
    User = get_user_model()
    nazov = models.CharField(max_length=64) 
    popis = models.TextField(null=True, blank=True)
    datum_konania = models.DateField() 
    ucastnici = models.ManyToManyField('Profil', related_name='prihlasene_udalosti', blank=True)
    
    TYP_CHOICES = [
        ('mission', 'Mission'),
        ('quest', 'Quest'),
        ('challange', 'Challange'),
        ('event', 'Event'),
        ('match', 'Match') ,
        ('battle', 'Battle'),
        ('duel', 'Duel'),
        ('raid', 'Raid'),
        ('tournament', 'Tournament'), 
        ('dungeon', 'Dungeon'),
    ]

    typ = models.CharField(max_length=64, choices=TYP_CHOICES) 
    
    organizator = models.ForeignKey(Profil, on_delete=models.SET_NULL, null=True, related_name='udalosti_organizovane')
    hra = models.ForeignKey(Hra, on_delete=models.CASCADE) 
    
    def __str__(self):
        return f"{self.nazov} ({self.typ})"

class Hodnotenie(models.Model):

    hodnotenie = models.IntegerField() 
    datum_hodnotenia = models.DateField(auto_now_add=True) 
    
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE) 
    hra = models.ForeignKey(Hra, on_delete=models.SET_NULL, null=True, blank=True)
    udalost = models.ForeignKey(Udalost, on_delete=models.SET_NULL, null=True, blank=True)
    
    # zabezpeci aby hodnotenie bolo len pre hru alebo udalost
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

class Oznamenie(models.Model):

    nazov = models.CharField(max_length=64) 
    
    TYP_CHOICES = [
        ('pozvanka', 'Pozvánka'), 
        ('upozornenie', 'Upozornenie'), 
        ('sprava', 'Správa'), 
    ]

    typ = models.CharField(max_length=64, choices=TYP_CHOICES) 
    obsah = models.TextField() 
    datum_vytvorenia = models.DateField(auto_now_add=True) 
    
    def __str__(self):
        return f"{self.nazov} ({self.typ})"

class Odoslanie(models.Model):
   
    oznamenie = models.ForeignKey(Oznamenie, on_delete=models.CASCADE)
    prijemca = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='prijate_oznamenia')
    
    datum_precitania = models.DateField(null=True, blank=True) 

    STAV_CHOICES = [
        ('neprecitane', 'Neprečítané'), 
        ('precitane', 'Prečítané'), 
    ]
    stav = models.CharField(max_length=64, choices=STAV_CHOICES, default='neprecitane') # enum, not null

    def __str__(self):
        return f"Oznámenie pre {self.prijemca.nickname} - {self.stav}"