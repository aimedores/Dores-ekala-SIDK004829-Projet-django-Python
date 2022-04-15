from django.urls import URLPattern, path, re_path
from . import views
from django.views.generic import TemplateView
import mptt_urls
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path('', views.Home.as_view(), name="home"),
    path('inscription', views.Signup.as_view(), name="inscription"),
    path('activation_compte/<uidb64>/<token>/',views.ActivationCompte.as_view(), name='activation_compte'),
    path('connexion', view=LoginView.as_view(template_name = "home/login.html", redirect_authenticated_user = True), name = "connexion"), 
    path('deconnexion', view=LogoutView.as_view(), name="deconnexion"),
]