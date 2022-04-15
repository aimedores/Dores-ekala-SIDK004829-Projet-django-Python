from django import forms
from django.forms import ModelForm
from .models import Panier
class PanierForm(ModelForm):
    class Meta:
        model = Panier
        fields = ['quantite']

CHOIX_PAYEMENT = (
    ('S', 'scripe'),
    ('P', 'paypal')
)

CHOIX_VILLE = (
    ('Brazzaville', 'Brazzaville'),
    ('Pointe-noire', 'Pointe-noire')
)


class CheckoutForm(forms.Form):
    adresse_livraison1 = forms.CharField(required=False)
    adresse_livraison2 = forms.CharField(required=False)
    ville_livraison = forms.ChoiceField(choices=CHOIX_VILLE)
    ville_livraison.widget.attrs.update({'class': 'country_select'})
    numero_telephone_livraison = forms.CharField(required=False)
    code_postal_livraison = forms.CharField(required=False)

    adresse_facturation1 = forms.CharField(required=False)
    adresse_facturation2 = forms.CharField(required=False)
    ville_facturation = forms.ChoiceField(choices=CHOIX_VILLE)
    ville_facturation.widget.attrs.update({'class': 'country_select'})
    numero_telephone_facturation = forms.CharField(required=False)
    code_postal_facturation = forms.CharField(required=False)

    meme_adresse_facturation = forms.BooleanField(required=False)
    adresse_livraison_par_defaut = forms.BooleanField(required=False)
    utiliser_adresse_livraison_par_defaut = forms.BooleanField(required=False)
    adresse_facturation_par_defaut = forms.BooleanField(required=False)
    utiliser_adresse_facturation_par_defaut = forms.BooleanField(required=False)

    option_payement = forms.ChoiceField(
        widget=forms.RadioSelect, choices=CHOIX_PAYEMENT)
