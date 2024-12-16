import json
import os


def carrega_json(arquivo_json):
    dados = ''
    with open(arquivo_json, 'r') as f:
        dados = json.load(f)
    return dados


# def processa1(dados):
#    # considera que o maior é igual ao menor
#    qtd_circs = len(dados.keys())
#    maior_circ = list(dados.values())[0]
#    menor_circ = list(dados.values())[0]
#
#    tamanho_circs = 0
#    for perm, circ in dados.items():
#        tam_circ = len(circ)
#        tamanho_circs += tam_circ
#
#        if tam_circ > len(maior_circ):
#            maior_circ = circ
#
#        if tam_circ < len(menor_circ):
#            menor_circ = circ
#
#    tamanho_medio = tamanho_circs / qtd_circs
#    return maior_circ, menor_circ, tamanho_medio

def processa(dados):
    d = sorted(dados, key=lambda k: len(dados[k]))
    qtd_circs = len(d)
    menor = dados[d[1]]
    maior = dados[d[-1]]

    tamanho_circs = 0
    for k in d:
        circ = dados[k]
        tamanho_circs += len(circ)

    tamanho_medio = tamanho_circs / qtd_circs
    return menor, maior, tamanho_medio


def busca_arquivos(diretorio='.', extensao='.json'):
    for d, subdiretorio, arquivo in os.walk(diretorio):
        for arq in sorted(arquivo):
            if arq.endswith(extensao):
                caminho = os.path.join(d, arq)
                yield caminho


if __name__ == '__main__':
    for arquivo in busca_arquivos():
        dados = carrega_json(arquivo)
        menor, maior, tam_medio = processa(dados)

        print(f'---------- {arquivo} ----------')
        print(f'menor({len(menor)}): {menor}')
        print(f'maior({len(maior)}): {maior}')
        print(f'tamanho médio = {tam_medio:.2f}\n')
