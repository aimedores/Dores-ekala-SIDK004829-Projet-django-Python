from django import forms
from django.forms import ModelForm, TextInput, PasswordInput, Textarea, EmailInput
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper


class InscriptionForm(UserCreationForm):
    class Meta:
        model = User
        widgets = {
           'first_name': TextInput(attrs={'placeholder': 'Votre prénom'}),
           'last_name': TextInput(attrs={'placeholder': 'Votre nom'}),
           'username': TextInput(attrs={'placeholder': 'Nom d\'utilisateur '}),
           'email': EmailInput(attrs={'placeholder': 'Adresse email'}),
           'password1': PasswordInput(attrs={'placeholder': 'Mot de passe'}),
           'password2': PasswordInput(attrs={'placeholder': 'Confirmer votre mot de passe'}),
       }
        fields = ('first_name', 'last_name','email', 'username', 'password1', 'password2')
        unlabelled_fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')
    def __init__(self, *args, **kwargs):
        super(InscriptionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        for field in InscriptionForm.Meta.unlabelled_fields:
            self.fields[field].label = False