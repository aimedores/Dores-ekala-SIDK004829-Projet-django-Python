from django.urls import URLPattern, path, re_path
from . import views

urlpatterns = [
    path('ajouter_au_panier/<slug>', views.ajouter_au_panier, name="ajouter_au_panier"),
    path('supprimer_du_panier/<slug:slug>', views.supprimer_du_panier, name="supprimer_du_panier"),
    path('panier', views.ArticlePanier.as_view(), name="panier"),
    path('checkout', views.CheckoutView.as_view(), name="checkout"), 
    path('payement/<option_payement>', views.PayementView.as_view(), name = "payement"),  
    path('confirmation_payement/<int:id>-<ref_code>', views.confirmation_payement, name = "confirmation_payement"), 
]