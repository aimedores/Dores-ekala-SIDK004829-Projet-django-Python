from django.shortcuts import render, HttpResponse
from django.views.generic import View, FormView
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


from articles.models import Article, Categorie
from .forms import InscriptionForm
from .token import activation_compte_token



class Home(View): 
    def get(self, request):
        articles = Article.objects.all().order_by('-id')
        categories = Categorie.objects.all()
        context = {
            'articles': articles,
            'categories': categories,
        }
        return render(request, 'home/index.html', context)

class Signup(FormView):
    template_name = 'home/inscription.html'
    form_class = InscriptionForm
    success_url = 'inscription'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        current_site = get_current_site(self.request)
        mail_subject = 'Activer votre compte.'
        message = render_to_string('home/mail_activation_compte.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': activation_compte_token.make_token(user),
        })
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )
        email.fail_silently = False
        email.send()

        messages.success(self.request, "Votre compte a été crée avec succes, Nous vous avons envoyez un email pour confirmer votre inscription")

        return super().form_valid(form)

class ActivationCompte(View):
    def get(self, request, uidb64, token):
        try:
            UserModel = get_user_model()
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and activation_compte_token.check_token(user, token):
            user.is_active = True
            user.save()
            return render(request,'home/validation_compte.html')
        else:
            return HttpResponse("Ce lien n'est plus valide!")