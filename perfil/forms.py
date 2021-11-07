from django.contrib.auth.models import User
from django import forms
from . import models


class PerfilForm(forms.ModelForm):
    class Meta:
        model = models.Perfil
        fields = '__all__'
        exclude = ('usuario', )


class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label='Senha',
        # help_text=''
    )

    password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label='Confirmação de senha'
    )

    def __init__(self, usuario=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.usuario = usuario

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'password', 'password2', 'email')

    def clean(self, *args, **kwargs):
        data = self.data
        cleaned = self.cleaned_data
        validation_error_msgs = {}

        # pegando valores digitados na tela
        usuario_data = cleaned.get('username')
        email_data = cleaned.get('email')
        password_data = cleaned.get('password')
        password2_data = cleaned.get('password2')

        # buscando na base pra verificar se existem
        novo_usuario = User.objects.filter(username=usuario_data).first()
        novo_email = User.objects.filter(email=email_data).first()

        # mensagens de validação
        error_msg_user_exists = 'Usuário já existe'
        error_msg_email_exists = 'E-mail já existe'
        error_msg_password_match = 'As duas senhas não conferem'
        error_msg_password_short = 'Sua senha precisa ter no mínimo 6 caracteres'
        error_msg_required_field = 'Este campo é obrigatório'

        # Usuario está logado: Atualizacao
        if self.usuario:
            # buscando informações do usuário logado
            usuario_logado = User.objects.filter(username=self.usuario).first()

            if novo_usuario:
                if usuario_logado.username != novo_usuario.username:
                    validation_error_msgs['username'] = error_msg_user_exists

            if novo_email:
                if usuario_logado.email != novo_email.email:
                    validation_error_msgs['email'] = error_msg_email_exists

            if password_data:
                if password_data != password2_data:
                    validation_error_msgs['password'] = error_msg_password_match
                    validation_error_msgs['password2'] = error_msg_password_match

                if len(password_data) < 6:
                    validation_error_msgs['password'] = error_msg_password_short
        else:
            # Usuario nao logado: Cadastro
            if novo_usuario:
                validation_error_msgs['username'] = error_msg_user_exists

            if novo_email:
                validation_error_msgs['email'] = error_msg_email_exists

            if not password_data:
                validation_error_msgs['password'] = error_msg_required_field

            if not password2_data:
                validation_error_msgs['password2'] = error_msg_required_field

            if password_data != password2_data:
                validation_error_msgs['password'] = error_msg_password_match
                validation_error_msgs['password2'] = error_msg_password_match

            if len(password_data) < 6:
                validation_error_msgs['password'] = error_msg_password_short

        if validation_error_msgs:
            raise(forms.ValidationError(validation_error_msgs))
