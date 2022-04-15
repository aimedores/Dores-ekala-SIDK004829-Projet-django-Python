from django.db import models
from django.conf import settings

# Create your models here.
class Panier(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete = models.CASCADE, verbose_name = "Utilisateur")
    article = models.ForeignKey('articles.Article', on_delete = models.CASCADE)
    quantite = models.IntegerField(default=0,verbose_name ="Quantité")
    commande = models.BooleanField(default=False,verbose_name ="Commandé")
    
    def __str__(self):
        return f" {self.quantite} article(s) de {self.article.plat}"

    def get_total_prix_article(self):
        return self.quantite * self.article.prix



class Commande(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete = models.CASCADE, verbose_name = "Utilisateur")
    ref_code = models.CharField(max_length=20, blank= True, null = True)
    articles = models.ManyToManyField(Panier, related_name="articles", verbose_name="Article")
    date_debut = models.DateTimeField(auto_now_add= True, verbose_name="Date de début")
    date_commande = models.DateTimeField(verbose_name="Date de commande")
    commande = models.BooleanField(default= False, verbose_name="Commandé")
    adresse_livraison = models.ForeignKey('Adresse', related_name="adresse_livraison", on_delete = models.SET_NULL, blank= True, null = True, verbose_name="Adresse de livraison" )
    adresse_facturation = models.ForeignKey('Adresse',related_name="adresse_facturation", on_delete = models.SET_NULL, blank= True, null = True, verbose_name="Adresse de facturation" )
    payement = models.ForeignKey('Payement',on_delete = models.SET_NULL, blank= True, null = True, verbose_name = "Payement")
    commande_livre = models.BooleanField(default= False, verbose_name="Livré")
    commande_recu = models.BooleanField(default= False, verbose_name="Réceptionné")
    confirmer_livraison = models.BooleanField(default= False, verbose_name="Confirmation de livraison")
    demande_remboursement = models.BooleanField(default= False, verbose_name="Remboursement demandé")
    remboursement_accorde = models.BooleanField(default= False, verbose_name="Remboursement accordé")

    def __str__(self):
        # pylint: disable=E1101
        return self.user.username

    def get_total_commande(self):
        total = 0
        for article_panier in self.articles.all():
            total += article_panier.get_total_prix_article()
        return total
    
    def get_total_final(self):
        return self.get_total_commande() + 4

CHOIX_ADRESSE = (
    ('L','livraison'),
    ('F','facturation')
)

class Adresse(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete = models.CASCADE, verbose_name="Utilisateur")
    adresse1 = models.CharField(max_length=100, verbose_name="Adresse 1")
    adresse2 = models.CharField(max_length=100, verbose_name="Adresse 2")
    ville = models.CharField(max_length=100)
    numero_telephone = models.CharField(max_length=50, verbose_name="Numéro de téléphone")
    code_postal = models.CharField(max_length=100, verbose_name="Code postal")
    type_adresse = models.CharField(max_length=1, choices=CHOIX_ADRESSE, verbose_name="type d'adresse")
    adresse_par_defaut = models.BooleanField(default=False, verbose_name="Adresse par défaut")



    def __str__(self):
        if self.user:
            return f'{self.user.username}'

class Payement(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    #commandes = models.ForeignKey('Commande',related_name="courses", on_delete = models.CASCADE, verbose_name="Commande")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete = models.CASCADE,verbose_name="Utilisateur" )
    montant_payement = models.FloatField(verbose_name="Montant")
    horodatage = models.DateTimeField(auto_now_add= True,verbose_name="horodatage")

    def __str__(self):
        if self.user:
            return f'{self.user.username}'
