from django.contrib import admin
from .models import Panier, Commande, Payement, Adresse

class PanierAdmin(admin.ModelAdmin):
    list_display = ['article','user','quantite']
    list_filter = ['user']

class CommandeAdmin(admin.ModelAdmin):
    list_display = ['user',
     'commande',
     'commande_livre',
     'commande_recu',
     'confirmer_livraison',
     'demande_remboursement',
     'remboursement_accorde',
     'adresse_facturation',
     'adresse_livraison',
     'payement',
     ]   

    list_filter = ['commande',
    'commande_livre',
    'commande_recu',
    'demande_remboursement',
    'remboursement_accorde'
    ]
    list_display_links = ['user',
    'adresse_facturation',
    'adresse_livraison',
    'payement',
    ]
    search_fields = ['user__username',
    'ref_code'
    ]

class AdresseAdmin(admin.ModelAdmin):
    list_display = ['user',
        'adresse1',
        'adresse2',
        'ville',
        'numero_telephone',
        'code_postal',
        'type_adresse',
        'adresse_par_defaut'
    ]
    
    list_filter = ['ville','type_adresse', 'adresse_par_defaut']

    search_fields = ['user','adresse1', 'adresse2', 'code_postal']

class PayementAdmin(admin.ModelAdmin):
    list_display = ['user', 'montant_payement', 'horodatage']
    readonly_fields = ['stripe_charge_id','user', 'montant_payement', 'horodatage']

admin.site.register(Panier, PanierAdmin)
admin.site.register(Commande, CommandeAdmin)
admin.site.register(Payement, PayementAdmin)
admin.site.register(Adresse, AdresseAdmin)
