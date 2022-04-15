from django.shortcuts import render,  redirect , get_object_or_404, HttpResponseRedirect, reverse
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from articles.models import Article
from .models import Panier, Commande, Adresse, Payement
from .forms import PanierForm, CheckoutForm


import random
import string
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required(login_url = 'connexion') 
def ajouter_au_panier(request, slug):
    article = get_object_or_404(Article, slug = slug)
    article_panier, created = Panier.objects.get_or_create(
            article = article,
            user = request.user,
            commande = False,
     )

    commande_qs = Commande.objects.filter(user = request.user, commande = False)

    if commande_qs.exists():
        commande = commande_qs[0]
        if commande.articles.filter(article__slug = article.slug).exists():
            if request.method == 'POST':  # if there is a post
                form = PanierForm(request.POST)
                if form.is_valid():
                    quantite = form.cleaned_data['quantite']
                    if quantite + article_panier.quantite > article_panier.article.quantite or article_panier.quantite >= article_panier.article.quantite:
                        messages.warning(request, "Désolé vous ne pouvez pas commander plus que la quantité disponible. Merci!")
                        return redirect('detail_article', slug = slug)
                    else:    
                        article_panier.quantite += quantite
                        article_panier.save()
                        messages.info(request, "La quantité de cet article a été mis à jour.")
                        return redirect('panier')
                else:
                    messages.warning(request, 'formulaire invalide')
                    return redirect('detail_article', slug = slug)
            else:
                return redirect('detail_article', slug = slug)
        else:
            if request.method == 'POST':  # if there is a post
                form = PanierForm(request.POST)
                if form.is_valid():
                    quantite = form.cleaned_data['quantite']
                    if quantite + article_panier.quantite > article_panier.article.quantite or quantite > article_panier.article.quantite:
                        messages.warning(request, "Désolé vous ne pouvez pas commander plus que la quantité disponible. Merci!")
                        return redirect('detail_article', slug = slug)
                    else:    
                        article_panier.quantite = quantite
                        article_panier.save()
                        commande.articles.add(article_panier)
                        messages.info(request, "Cet article a été ajouté à votre panier.")
                        return redirect('panier')
                else:
                    messages.warning(request, 'formulaire invalide')
                    return redirect('detail_article', slug = slug)
            else:
                return redirect('detail_article', slug = slug)
            
    else:
        date_commande = timezone.now()
        commande = Commande.objects.create(user = request.user, date_commande = date_commande)
        if request.method == 'POST':  # if there is a post
            form = PanierForm(request.POST)
            if form.is_valid():
                quantite = form.cleaned_data['quantite']
                if quantite + article_panier.quantite > article_panier.article.quantite or quantite >= article_panier.article.quantite:
                    messages.warning(request, "Désolé vous ne pouvez pas commander plus que la quantité disponible. Merci!")
                    return redirect('detail_article', slug = slug)
                else:    
                    article_panier.quantite = quantite
                    article_panier.save()
                    commande.articles.add(article_panier)
                    messages.info(request, "Cet article a été ajouté à votre panier.")
                    return redirect('panier')
            else:
                messages.warning(request, 'formulaire invalide')
                return redirect('detail_article', slug = slug)
        else:
            return redirect('detail_article', slug = slug)


@login_required(login_url = 'connexion') 
def supprimer_du_panier(request, slug):
    article = get_object_or_404(Article, slug = slug)
    commande_qs = Commande.objects.filter(user = request.user, commande = False)

    if commande_qs.exists():
        commande = commande_qs[0]
        if commande.articles.filter(article__slug = article.slug).exists():
            article_panier = Panier.objects.filter(
                article = article,
                user = request.user,
                commande = False,
            )[0]
            commande.articles.remove(article_panier)
            article_panier.delete()

            messages.info(request, "Cet article a été retiré de votre panier..")
            return redirect('panier')
        else:
            messages.info(request, "Cet article n'existe pas dans votre panier.")
            return redirect('/')
    else:
        messages.info(request, "Vous n'avez pas d'ordre d'achat")
        return redirect('detail_article', slug = slug)


class ArticlePanier(LoginRequiredMixin, View):
    def get(self, request):
        try:
            commande = Commande.objects.filter(user = request.user, commande = False).order_by('articles__id').first()
            context = {
                'commande':commande,
            }
            return render(request, "articles/panier.html", context)

        except ObjectDoesNotExist:
            messages.warning(request, "Vous n'avez aucun article dans le panier")
            return redirect("/")


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            
            commande = Commande.objects.get(user = self.request.user, commande = False) 
            art = commande.articles.all()
            if not art:
                return redirect('home')
            else: 
                form = CheckoutForm()
                context = {
                    'form' : form,
                    'commande' : commande,
                }
                
                adresse_livraison_qs = Adresse.objects.filter(
                    user = self.request.user,
                    type_adresse = "L",
                    adresse_par_defaut = True
                )
                if adresse_livraison_qs.exists():
                    context.update(
                        {'adresse_livraison_par_defaut': adresse_livraison_qs.last()})

                adresse_facturation_qs = Adresse.objects.filter(
                    user = self.request.user,
                    type_adresse = "F",
                    adresse_par_defaut = True
                )
                if adresse_facturation_qs.exists():
                    context.update({'adresse_facturation_par_defaut': adresse_facturation_qs.last()})

                return render(self.request, 'commande/checkout.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "Vous n'avez pas d'ordre d'achat")
            return redirect("home")
        
    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            commande = Commande.objects.get(user = self.request.user, commande = False)
            if form.is_valid():
                utiliser_adresse_livraison_par_defaut = form.cleaned_data.get('utiliser_adresse_livraison_par_defaut')
                if utiliser_adresse_livraison_par_defaut:
                    adresse_qs = Adresse.objects.filter(
                    user = self.request.user,
                    type_adresse = "L",
                    adresse_par_defaut = True
                    )
                    if adresse_qs.exists():
                        adresse_livraison = adresse_qs.last()
                        commande.adresse_livraison = adresse_livraison
                        commande.save()
                    else:
                        messages.warning(self.request, "Aucune adresse de livraison par défaut disponible")
                        return redirect('checkout')

                else:
                    adresse_livraison1 = form.cleaned_data.get('adresse_livraison1')
                    adresse_livraison2 = form.cleaned_data.get('adresse_livraison2')
                    ville_livraison = form.cleaned_data.get('ville_livraison')
                    numero_telephone_livraison = form.cleaned_data.get('numero_telephone_livraison')
                    code_postal_livraison = form.cleaned_data.get('code_postal_livraison')
                    if is_valid_form([adresse_livraison1, ville_livraison, numero_telephone_livraison, code_postal_livraison]):
                        adresse_livraison = Adresse(
                            user = self.request.user,
                            adresse1 = adresse_livraison1,
                            adresse2 = adresse_livraison2,
                            ville = ville_livraison,
                            numero_telephone = numero_telephone_livraison,
                            code_postal  = code_postal_livraison,
                            type_adresse="L"
                        )
                        adresse_livraison.save()
                        commande.adresse_livraison = adresse_livraison
                        commande.save()

                        adresse_livraison_par_defaut = form.cleaned_data.get('adresse_livraison_par_defaut')
                        if adresse_livraison_par_defaut:
                            adresse_livraison.adresse_par_defaut = True
                            adresse_livraison.save()
                    else:
                        messages.warning(self.request, "veuillez remplir les champs d'adresse de livraison requis")
                        return redirect('checkout')
                
                utiliser_adresse_facturation_par_defaut = form.cleaned_data.get('utiliser_adresse_facturation_par_defaut')
                meme_adresse_facturation = form.cleaned_data.get('meme_adresse_facturation')

                if meme_adresse_facturation:
                    adresse_facturation = adresse_livraison
                    adresse_facturation.pk = None
                    adresse_facturation.save()
                    adresse_facturation.type_adresse = "F"
                    adresse_facturation.save()
                    commande.adresse_facturation = adresse_facturation
                    commande.save()

                elif utiliser_adresse_facturation_par_defaut:
                    adresse_qs = Adresse.objects.filter(
                    user = self.request.user,
                    type_adresse = "F",
                    adresse_par_defaut = True
                    )
                    if adresse_qs.exists():
                        adresse_facturation = adresse_qs.last()
                        commande.adresse_facturation = adresse_facturation
                        commande.save()
                    else:
                        messages.warning(self.request, "Aucune adresse de facturation par défaut disponible")
                        return redirect('checkout')

                else:
                    adresse_facturation1 = form.cleaned_data.get('adresse_facturation1')
                    adresse_facturation2 = form.cleaned_data.get('adresse_facturation2')
                    ville_facturation = form.cleaned_data.get('ville_facturation')
                    numero_telephone_facturation = form.cleaned_data.get('numero_telephone_facturation')
                    code_postal_facturation = form.cleaned_data.get('code_postal_facturation')

                    if is_valid_form([adresse_facturation1, ville_facturation, numero_telephone_facturation, code_postal_facturation]):
                        adresse_facturation = Adresse(
                            user = self.request.user,
                            adresse1 = adresse_facturation1,
                            adresse2 = adresse_facturation2,
                            ville = ville_facturation,
                            numero_telephone = numero_telephone_facturation,
                            code_postal  = code_postal_facturation,
                            type_adresse="F"
                        )
                        adresse_facturation.save()
                        commande.adresse_facturation = adresse_facturation
                        commande.save()

                        adresse_facturation_par_defaut = form.cleaned_data.get('adresse_facturation_par_defaut')
                        if adresse_facturation_par_defaut:
                            adresse_facturation.adresse_par_defaut = True
                            adresse_facturation.save()
                    else:
                        messages.warning(self.request, "veuillez remplir les champs d'adresse de facturation requis")
                        return redirect('checkout')

                option_payement = form.cleaned_data.get('option_payement')

                if option_payement == "S":
                    return redirect('payement', option_payement = "scripe")
                elif option_payement == "P":
                    return redirect('payement', option_payement = "paypal")
                else:
                    messages.warning(self.request, "Mauvais choix de payement")
                    return redirect('checkout')
            else:
                messages.warning(self.request, "formulaire invalide")
                return redirect('checkout')

        except ObjectDoesNotExist:
            messages.warning(self.request, "Vous n'avez pas d'ordre d'achat")
            return redirect("panier")

def creer_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k= 20))

class PayementView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            commande = Commande.objects.get(user = self.request.user, commande = False) 
            if commande.adresse_facturation :
                context = {
                    'commande' : commande,
                }   
                return render(self.request,'commande/payement.html', context)
            else:
                messages.warning(self.request, "Vous n'avez pas ajouté une adresse de facturation")
                return redirect("checkout")
        except ObjectDoesNotExist:
            messages.info(self.request, "Vous n'avez pas d'ordre d'achat")
            return redirect('/')
        

    def post(self, *args, **kwargs):
        
        commande = Commande.objects.get(user = self.request.user, commande = False)    
        token = self.request.POST.get('stripeToken')
        montant = int(commande.get_total_commande() * 100)

        try:
            charge = stripe.Charge.create(
            amount=montant,
            currency="usd",
            source=token
            )

            #creation du payement
            payement = Payement()
            payement.stripe_charge_id = charge['id']
            payement.user = self.request.user
            payement.montant_payement = commande.get_total_final()
            payement.save()

            """
            article_panier = Panier.objects.filter(user = self.request.user, commande = False)
            for article in article_panier:
                detail_commande = ArticleCommande()
                detail_commande.commande_id = commande.id
                detail_commande.user = self.request.user
                detail_commande.article_id = article.article_id
                detail_commande.variante_id = article.variante.id
                detail_commande.quantite = article.quantite
                detail_commande.image_id = article.variante.image_id1
                if article.variante.prix_reduction:
                    detail_commande.prix = article.variante.prix_reduction
                else:
                    detail_commande.prix = article.variante.prix
                detail_commande.total = article.get_prix_final()
                detail_commande.total_commande = commande.get_total_final()
                detail_commande.save()
            """
                
            articles_panier = commande.articles.all()
            articles_panier.update(commande = True)
            for article in articles_panier:
                article.save()
            commande.commande = True
            commande.payement = payement
            commande.ref_code = creer_ref_code()

            commande.save()

            """
            for rs in article_panier:
                if rs.article.variante !='None':
                    variante = Variante.objects.get(id=rs.variante_id)
                    variante.quantite -= rs.quantite
                    variante.nombre_vente += rs.quantite
                    variante.save()
            """

            messages.success(self.request, "Votre payement a été bien effectué!")
            """
            detail_commande = Commande.objects.filter(user = self.request.user, commande = True, ref_code = commande.ref_code)
            article_commande = Panier.objects.filter( articles__pk = commande.id, user=self.request.user, commande = True)
            context2 = {
                'detail_commande' : detail_commande,
                'article_commande' : article_commande,
                'name' : self.request.user.first_name
            }
            
            html_content = render_to_string('email_template.html', context2)
            text_content = strip_tags(html_content)
            
            email = EmailMultiAlternatives(
                'Confirmation de la commande',
                text_content,
                settings.EMAIL_HOST_USER,
                [self.request.user.email]
            )
            email.fail_silently = False
            email.attach_alternative(html_content, "text/html")
            email.send()
            """
            url = reverse('confirmation_payement', kwargs={'id': commande.id,'ref_code': commande.ref_code })
            return HttpResponseRedirect(url)

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error',{})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect('/')

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Erreur de limite de taux")
            return redirect('/')

        except stripe.error.InvalidRequestError as e:
            messages.warning(self.request, "Paramètres invalides")
            return redirect('/')

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, "Vous n'êtes pas authentifié ")
            return redirect('/')

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, "Erreur réseau")
            return redirect('/')

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(self.request, "Quelque chose s'est mal passé, vous n'êtes pas accusé. Veuillez réessayer")
            return redirect('/')

        except Exception as e:
            # envoyer un email par nous même
            messages.warning(self.request, "Une erreur grave s'est produite, nous avons été informés")
            return redirect('/')
 
def confirmation_payement(request,id, ref_code):
    commande = Commande.objects.filter(user = request.user, commande = True, ref_code = ref_code)
    #article_commande = ArticleCommande.objects.filter( commande__pk = id,commande__ref_code = ref_code, user=request.user, commande__commande = True)
    context = {
        'commande' : commande,
        #'article_commande' : article_commande,
    }

    return render(request, "commande/confirmation_payement.html", context)