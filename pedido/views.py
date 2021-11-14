from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView
from django.contrib import messages
from produto.models import Variacao
from .models import Pedido, ItemPedido
from utils import utils


class Pagar(View):
    template_name = 'pedido/pagar.html'

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'Você precisa fazer login.')
            return redirect('perfil:criar')

        if not self.request.session.get('carrinho'):
            messages.error(self.request, 'Carrinho vazio.')
            return redirect('produto:lista')

        carrinho = self.request.session.get('carrinho')
        carrinho_variacao_ids = [vid for vid in carrinho]
        bd_variacoes = list(Variacao.objects.select_related('produto').filter(
            id__in=carrinho_variacao_ids))

        estoque_insuficiente = False
        for variacao in bd_variacoes:
            vid = str(variacao.id)
            estoque = variacao.estoque

            qtd_carrinho = carrinho[vid]['quantidade']
            preco_unt = carrinho[vid]['preco_unitario']
            preco_unt_promo = carrinho[vid]['preco_unitario_promocional']

            if estoque < qtd_carrinho:
                # diminuir qtd do carrinho
                carrinho[vid]['quantidade'] = estoque
                carrinho[vid]['preco_quantitativo'] = estoque * preco_unt
                carrinho[vid]['preco_quantitativo_promocional'] = estoque * \
                    preco_unt_promo

                estoque_insuficiente = True

        if estoque_insuficiente:
            messages.error(
                self.request,
                'Estoque insuficiente para alguns produtos do seu carrinho. '
                'Reduzimos a quantidade desses produtos. Verifique seu carrinho. '
            )
            self.request.session.save()
            return redirect('produto:carrinho')

        qtd_total_carrinho = utils.qtd_total_carrinho(carrinho)
        valor_total_carrinho = utils.total_carrinho(carrinho)

        # Criando pedido
        pedido = Pedido(
            usuario=self.request.user,
            total=valor_total_carrinho,
            status='C',
            qtd_total=qtd_total_carrinho
        )
        pedido.save()

        ItemPedido.objects.bulk_create(
            [
                ItemPedido(
                    pedido=pedido,
                    produto=v['produto_nome'],
                    produto_id=v['produto_id'],
                    variacao=v['variacao_nome'],
                    variacao_id=v['variacao_id'],
                    preco=v['preco_quantitativo'],
                    preco_promocional=v['preco_quantitativo_promocional'],
                    quantidade=v['quantidade'],
                    imagem=v['imagem'],
                ) for v in carrinho.values()
            ]
        )

        del self.request.session['carrinho']
        contexto = {
            'pedido': pedido
        }

        return render(self.request, self.template_name, contexto)


class SalvarPedido(View):
    pass


class Detalhe(View):
    pass


class Lista(View):
    pass
