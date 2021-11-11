from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views import View
from django.contrib.auth.models import User
import copy
from django.contrib.auth import authenticate, login, logout
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
                    instance=self.request.user  # envia instancia pro formulario
                ),
                'perfilform': forms.PerfilForm(
                    data=self.request.POST or None,
                    instance=self.perfil  # envia instancia pro formulario
                )
            }
        else:
            self.contexto = {
                'userform': forms.UserForm(data=self.request.POST or None),
                'perfilform': forms.PerfilForm(data=self.request.POST or None)
            }

        self.user_form = self.contexto['userform']
        self.perfil_form = self.contexto['perfilform']

        # caso o usuário esteja logado, manda pra pagina de atualizar
        if self.request.user.is_authenticated:
            self.template_name = 'perfil/atualizar.html'

        self.renderizar = render(
            self.request, self.template_name, self.contexto)

    def get(self, *args, **kwargs):
        return self.renderizar


class Criar(BasePerfil):
    def post(self, *args, **kwargs):
        if not self.user_form.is_valid() or not self.perfil_form.is_valid():
            messages.error(
                self.request, 'Existem erros no formulário enviado, por favor verifique os campos.')
            return self.renderizar

        username = self.user_form.cleaned_data.get('username')
        password = self.user_form.cleaned_data.get('password')
        email = self.user_form.cleaned_data.get('email')
        first_name = self.user_form.cleaned_data.get('first_name')
        last_name = self.user_form.cleaned_data.get('last_name')

        # Usuario logado -> Atualiza
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

            # se o usuário estar cadastrado mas nao tiver perfil
            if not self.perfil:
                self.perfil_form.cleaned_data['usuario'] = usuario
                perfil = models.Perfil(**self.perfil_form.cleaned_data)
            else:
                perfil = self.perfil_form.save(commit=False)
                perfil.usuario = usuario

            perfil.save()

            msg_retorno = 'Cadastro atualizado com sucesso.'
        else:
            # Usuario novo -> Criar
            usuario = self.user_form.save(commit=False)
            usuario.set_password(password)  # criptografa senha
            usuario.save()

            perfil = self.perfil_form.save(commit=False)
            perfil.usuario = usuario
            perfil.save()

            msg_retorno = 'Cadastro criado com sucesso. Você já está logado e pode concluir sua compra.'

        if password:
            # verifica se usuario e senha autentica
            autentica = authenticate(
                self.request,
                username=usuario,
                password=password,
            )
            # loga o usuario
            if autentica:
                login(self.request, user=usuario)

        self.request.session['carrinho'] = self.carrinho
        self.request.session.save()

        messages.success(self.request, msg_retorno)
        return redirect('produto:carrinho')


class Login(View):
    def post(self, *args, **kwargs):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')

        if not username or not password:
            messages.error(self.request, 'Você deve informar usuário e senha.')
            return redirect('perfil:criar')

        usuario = authenticate(
            self.request, username=username, password=password)

        if not usuario:
            messages.error(self.request, 'Usuário e/ou senha inválidos.')
            return redirect('perfil:criar')

        login(self.request, user=usuario)
        messages.success(self.request, 'Você está logado!')
        return redirect('produto:carrinho')


class Logout(View):
    def get(self, *args, **kwargs):
        carrinho = copy.deepcopy(self.request.session.get('carrinho', {}))
        logout(self.request)

        self.request.session['carrinho'] = carrinho
        self.request.session.save()

        return redirect('produto:lista')
