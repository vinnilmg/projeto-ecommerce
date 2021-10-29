import re
import os
from django.conf import settings
from PIL import Image


def formata_preco(val):
    return f'R$ {val:.2f}'.replace('.', ',')


def resize_image(img, new_width=800):
    img_full_path = os.path.join(settings.MEDIA_ROOT, img.name)
    img_pil = Image.open(img_full_path)
    original_width, original_height = img_pil.size

    if original_width <= new_width:
        print('Retornando largura original menor/igual que nova largura')
        img_pil.close()
        return

    new_height = round((new_width * original_height) / original_width)

    new_img = img_pil.resize((new_width, new_height), Image.LANCZOS)
    new_img.save(
        img_full_path,
        optimize=True,
        quality=50
    )
    print('Imagem redimensionada.')


def valida_cpf(cpf):
    cpf = str(cpf)
    cpf = re.sub(r'[^0-9]', '', cpf)

    if not cpf or len(cpf) != 11:
        return False

    # Elimina os dois últimos digitos do CPF
    novo_cpf = cpf[:-2]
    reverso = 10                        # Contador reverso
    total = 0

    # Loop do CPF
    for index in range(19):
        if index > 8:                   # Primeiro índice vai de 0 a 9,
            index -= 9                  # São os 9 primeiros digitos do CPF

        total += int(novo_cpf[index]) * reverso  # Valor total da multiplicação

        reverso -= 1                    # Decrementa o contador reverso
        if reverso < 2:
            reverso = 11
            d = 11 - (total % 11)

            if d > 9:                   # Se o digito for > que 9 o valor é 0
                d = 0
            total = 0                   # Zera o total
            novo_cpf += str(d)          # Concatena o digito gerado no novo cpf

    # Evita sequencias. Ex.: 11111111111, 00000000000...
    sequencia = novo_cpf == str(novo_cpf[0]) * len(cpf)

    # Descobri que sequências avaliavam como verdadeiro, então também
    # adicionei essa checagem aqui
    if cpf == novo_cpf and not sequencia:
        return True
    else:
        return False


def qtd_total_carrinho(carrinho):
    return sum([item['quantidade'] for item in carrinho.values()])


def total_carrinho(carrinho):
    return sum(
        [
            item.get('preco_quantitativo_promocional') if item.get(
                'preco_quantitativo_promocional') else item.get('preco_quantitativo')
            for item in carrinho.values()
        ]
    )
