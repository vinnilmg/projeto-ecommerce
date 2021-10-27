from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.contrib import messages
from . import models
from pprint import pprint


class ListaProdutos(ListView):
    model = models.Produto
    template_name = 'produto/lista.html'
    context_object_name = 'produtos'
    paginate_by = 10


class DetalheProduto(DetailView):
    model = models.Produto
    template_name = 'produto/detalhe.html'
    context_object_name = 'produto'
    slug_url_kwargs = 'slug'


class AdicionarAoCarrinho(View):
    def get(self, *args, **kwargs):

        # TODO: deletar carrinho da session
        # if self.request.session.get('carrinho'):
        #     del self.request.session['carrinho']
        #     self.request.session.save()

        # url anterior
        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('produto:lista')
        )
        variacao_id = self.request.GET.get('vid')

        # verifica se foi passado o id da variacao
        if not variacao_id:
            messages.error(self.request, 'Produto não existe')
            return redirect(http_referer)

        # busca objeto
        variacao = get_object_or_404(models.Variacao, id=variacao_id)

        # verifica se tem estoque
        if variacao.estoque < 1:
            messages.error(self.request, 'Estoque insuficiente')
            return redirect(http_referer)

        # verifica se tem carrinho na session
        if not self.request.session.get('carrinho'):
            self.request.session['carrinho'] = {}
            self.request.session.save()

        carrinho = self.request.session['carrinho']

        sem_estoque = False
        if variacao_id in carrinho:
            quantidade_carrinho = carrinho[variacao_id]['quantidade']
            quantidade_carrinho += 1

            # nao tem estoque suficiente
            if variacao.estoque < quantidade_carrinho:
                sem_estoque = True
                quantidade_carrinho = variacao.estoque

            carrinho[variacao_id]['quantidade'] = quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo'] = round(
                variacao.preco * quantidade_carrinho, 2)

            carrinho[variacao_id]['preco_quantitativo_promocional'] = round(
                variacao.preco_promocional * quantidade_carrinho, 2)
        else:
            carrinho[variacao_id] = {
                'produto_id': variacao.produto.id,
                'produto_nome': variacao.produto.nome,
                'variacao_nome': variacao.nome or '',
                'variacao_id': variacao.id,
                'preco_unitario': variacao.preco,
                'preco_unitario_promocional': variacao.preco_promocional,
                'preco_quantitativo': variacao.preco,
                'preco_quantitativo_promocional': variacao.preco_promocional,
                'quantidade': 1,
                'slug': variacao.produto.slug,
                'imagem': variacao.produto.imagem.name or ''
            }
        self.request.session.save()
        # pprint(carrinho)

        if not sem_estoque:
            messages.success(
                self.request,
                f'Produto {variacao.produto.nome} - {variacao.nome or ""} adicionado ao seu carrinho {carrinho[variacao_id]["quantidade"]}x.'
            )
        else:
            messages.warning(self.request,
                             f'Estoque insuficiente para {quantidade_carrinho}x no produto "{variacao.produto.nome}". '
                             f'Adicionamos {variacao.estoque}x no seu carrinho.'
                             )

        return redirect(http_referer)


class RemoverDoCarrinho(View):
    pass


class Carrinho(View):
    def get(self, request, *args, **kwargs):
        return render(self.request, 'produto/carrinho.html')


class Finalizar(View):
    pass
