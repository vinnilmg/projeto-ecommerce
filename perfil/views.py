from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.views import View
from django.contrib.auth.models import User
import copy
from . import models
from . import forms


class BasePerfil(View):
    template_name = 'perfil/criar.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        self.carrinho = copy.deepcopy(self.request.session.get('carrinho', {}))

        self.perfil = None

        if self.request.user.is_authenticated:
            self.perfil = models.Perfil.objects.filter(
                usuario=self.request.user).first()

            self.contexto = {
                'userform': forms.UserForm(
                    data=self.request.POST or None,
                    usuario=self.request.user,
                    instance=self.request.user
                ),
                'perfilform': forms.PerfilForm(
                    data=self.request.POST or None,
                    # perfil=self.perfil
                )
            }
        else:
            self.contexto = {
                'userform': forms.UserForm(data=self.request.POST or None),
                'perfilform': forms.PerfilForm(data=self.request.POST or None)
            }

        self.user_form = self.contexto['userform']
        self.perfil_form = self.contexto['perfilform']

        self.renderizar = render(
            self.request, self.template_name, self.contexto)

    def get(self, *args, **kwargs):
        return self.renderizar


class Criar(BasePerfil):
    def post(self, *args, **kwargs):
        if not self.user_form.is_valid() or not self.perfil_form.is_valid():
            return self.renderizar

        username = self.user_form.cleaned_data.get('username')
        password = self.user_form.cleaned_data.get('password')
        email = self.user_form.cleaned_data.get('email')
        first_name = self.user_form.cleaned_data.get('first_name')
        last_name = self.user_form.cleaned_data.get('last_name')

        if self.request.user.is_authenticated:
            usuario = get_object_or_404(
                User, username=self.request.user.username)

            usuario.username = username
            usuario.email = email
            usuario.first_name = first_name
            usuario.last_name = last_name

            if password:
                usuario.set_password(password)

            usuario.save()
        else:
            usuario = self.user_form.save(commit=False)
            usuario.set_password(password)  # criptografa senha
            usuario.save()

            perfil = self.perfil_form.save(commit=False)
            perfil.usuario = usuario
            perfil.save()

        self.request.session['carrinho'] = self.carrinho
        self.request.session.save()
        return self.renderizar


class Atualizar(View):
    pass


class Login(View):
    pass


class Logout(View):
    pass
