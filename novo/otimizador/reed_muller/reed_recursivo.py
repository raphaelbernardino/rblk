from typing import List

from rich.traceback import install

from novo.logs.logging_utils import create_logger
from novo.otimizador.reed_muller.util_reed import determina_quantidades_de_bits, gera_string_binaria_equivalente, \
    executa_linha, sanitiza_permutacao

install(show_locals=True)

logger = create_logger(name='reed_recursivo', level='DEBUG')

XOR = '⊕'
VAZIO = 'Ø'


def conta_quantidade_de_portas(expressao):
    return expressao.count(f'{XOR}')


def gera_estados(n: int, alvos: List[int], prefixo: str = 'x'):
    """
    Gera a lista de estados referente ao circuito desejado.

    :param n: Indica a quantidade de linhas que o circuito possui.
    :param alvos: Indica as linhas que representam os alvos existentes.
    :param prefixo: Qual deve ser o prefixo dos estados gerados?
    :return: Uma lista de estados contendo todas as linhas que não são alvos.
    """
    estados = []

    for i in range(0, n + 0):
        estado = f'{prefixo}{i}'

        if i not in alvos:
            estados.append(estado)

    return estados


# def gera_estados(n, prefixo='x'):
#     estados = [f'{prefixo}{n}' for n in range(1, n+1)]
#
#     return estados


def particiona_permutacao(dh, k=0, n=None):
    """
        Divide o DH particionando através do elemento fixo K.
    """
    if n is None:
        n = determina_quantidades_de_bits(dh)

    dh1 = list()
    dh2 = list()

    for i, h in enumerate(dh):
        r = f'{i:b}'.zfill(n)

        if r[k] == '0':
            dh1.append(h)
        else:
            dh2.append(h)

    return [dh1, dh2]


# def processa_permutacao(g, n, estados, nivel=0, prefixo='x', valor_inicial=1):
def processa_permutacao(g, n, estados, nivel=0, prefixo='x', alvo=0):
    return processa_permutacao_aux(g, n, estados, nivel, prefixo, alvo)


# n: quantidade de bits (inclui o alvo?) supomos que sim
def processa_permutacao_aux(g, n, estados, nivel=0, prefixo='x', alvo=0):
    # logger.debug(f'Entrando na recursão nível {nivel}')

    # se DH possui apenas 1, então termina (equação é igual a 1)
    if g.count(1) == len(g):
        # logger.debug(f'Encontrei uma G sem entrada nula')
        return f'1'

    # se DH está zerado, então termina (equação vazia)
    if [0] * len(g) == g:
        # logger.debug(f'Equação (zerada) == {g}')
        return f'{VAZIO}'

    if g.count(1) < 2:
        # logger.debug(f'Encontrei uma G com apenas uma entrada não nula')
        posicao = g.index(1)
        logger.debug(f'Encontrei a única entrada não nula na posição {posicao}')
        str_bin = gera_string_binaria_equivalente(posicao, estados, n, gerar_negativos=True, alvo=alvo)
        logger.debug(f'A string binária equivalente é: {str_bin}')
        equacao = ' . '.join(str_bin)
        logger.debug(f'Logo, a minha equação equivalente é: {equacao}')

        return equacao

    # se DH tem menos de dois elementos, então termina
    if len(g) < 2:
        # logger.debug(f'Equação (tam<2) == {g}')
        # return f'?'
        return f'1'

    metade_tamanho = len(g) // 2
    primeira_metade_g = g[0:metade_tamanho]
    segundo_metade_g = g[metade_tamanho:len(g)]
    if primeira_metade_g == segundo_metade_g:
        novos_estados = estados[:]
        del novos_estados[0]

        v = processa_permutacao_aux(g=primeira_metade_g, n=n - 1, estados=novos_estados, nivel=nivel + 1,
                                    prefixo=prefixo, alvo=alvo)

        return v

    espacos = '   ' * nivel
    _, eqd, dh = executa_linha(g, estados, nivel, alvo=alvo - nivel)
    logger.debug(f'Encontrei uma Equação {eqd} com DH = {dh}')

    # Equação total (ou final) --- resposta da recursão
    eqt = []

    # se a equação encontra neste nível da recursão é vazia, ou
    # se a equação é simplesmente igual a 1, dai retorna vazio
    # c.c. junta a equação encontrada neste nível com a equação anterior (encontrada nos niveis acima)
    if eqd == '' or eqd.strip() == '1':
        eqd = f'{VAZIO}'
    else:
        eqt.append(eqd)

    if dh.count(1) == 1:
        # logger.debug(f'\t\t\tDH:{dh}')

        # logger.debug(f'\t*\tfinal: {v0} &\t {v1}')
        idx = dh.index(1)
        valor_str = f'{idx:b}'.zfill(n)
        # logger.debug(f'IDX - valor str:{valor_str}')

        posicao = dh.index(1)
        logger.debug(f'Encontrei em DH a única entrada não nula na posição {posicao}')
        str_bin = gera_string_binaria_equivalente(posicao, estados, n, gerar_negativos=True, alvo=alvo)
        logger.debug(f'A string binária de DH equivalente é: {str_bin}')
        eqd = ' . '.join(str_bin)
        logger.debug(f'Logo, a minha equação de DH equivalente é: {eqd}')

        eqt.append(eqd)

        eq = f' {XOR} '.join(eqt)
        return eq

    n -= 1

    ##### REMOVER DEPOIS
    eq1 = ''
    eq2 = ''
    #####

    # logger.debug(f'n:{n}')
    if dh != [0] * n:
        # se novo DH não está zerado, particiona
        g1, g2 = particiona_permutacao(dh, k=0)

        # logger.debug(f'{espacos}EQ_D{nivel} = {eqd}')
        # logger.debug(f'{espacos}FP{nivel} = {eqd}')
        # logger.debug(f'{espacos}Particionando F{nivel} = {dh} em F{nivel + 1} = {g1} e F{nivel + 1}\' = {g2}')

        # estados_temp = estados[:alvo] + estados[alvo+1:]
        estados_temp = estados[1:]
        # logger.debug(f'{L=} {i=} {Ltemp=}')

        ind = estados[0]

        # logger.debug(f'       tbl_vdd = {dh} \t\t qtd_1s = {dh.count(1)}')
        # logger.debug(f'       tbl_g1 = {g1} \t\t qtd_1s = {g1.count(1)}')
        # logger.debug(f'       tbl_g2 = {g2} \t\t qtd_1s = {g2.count(1)}')

        # antes o parâmetro era n-1
        v0 = processa_permutacao_aux(g1, n, estados_temp, nivel + 1, prefixo, alvo - nivel)
        # logger.debug(f'{"---" * nivel}expr_F{nivel + 1} = {v0}')

        # antes o parâmetro era n-1
        v1 = processa_permutacao_aux(g2, n, estados_temp, nivel + 1, prefixo, alvo - nivel)
        # logger.debug(f'{"---" * nivel}expr_F{nivel + 1}\'= {v1}')

        # logger.debug(f'n:{n}')

        # logger.debug(f'V0 = {v0}')
        # logger.debug(f'V1 = {v1}')

        if v0 == '1':
            eq1 = f' ~{ind} '
            eqt.append(eq1)

        elif v0 != f'{VAZIO}':
            eq1t = list()
            for variavel in v0.split(f'{XOR}'):
                variavel = variavel.strip()
                eq1t.append(f' ~{ind} . {variavel}')

            eq1 = f' {XOR} '.join(eq1t)
            # logger.debug(f'EQ1 ==> {eq1} :: EQ1T ==> {eq1t}')

            # eq1 = f' ~{ind} . ( ' + str(v0) + ' )'
            eqt.append(eq1)

        if v1 == '1':
            eq2 = f' {ind} '
            eqt.append(eq2)

        elif v1 != f'{VAZIO}':
            eq2t = list()
            for variavel in v1.split(f'{XOR}'):
                variavel = variavel.strip()
                eq2t.append(f' {ind} . {variavel}')

            eq2 = f' {XOR} '.join(eq2t)
            # logger.debug(f'EQ2 ==> {eq2} :: EQ2T ==> {eq2t}')

            # eq2 = f' {ind} . ( ' + str(v1) + ' )'
            eqt.append(eq2)

    # logger.debug(f'{eq1=}')
    # logger.debug(f'{eq2=}')
    # logger.debug(f'{eqt=}')

    eq = f' {XOR} '.join(eqt)
    # logger.debug(f'{espacos}FT{nivel} = {eq}')

    return eq


# def executa(permutacoes, debug=False):
#     # if bool(debug):
#     #     logging.getLogger().setLevel(logging.DEBUG)
#
#     # '''
#     linha = [0, 0, 0, 0, 0, 1, 1, 1]
#
#     n = determina_quantidades_de_bits(linha)
#     estados = gera_estados(n)
#     # eq = processa_permutacao(linha, n, estados)
#     eq = processa_permutacao(linha, n, estados, alvo=0)
#     logger.debug(f'Equacao Encontrada = {eq}')
#     r = avalia_expressao(eq, identificador='x', nbits=n, estados=estados)
#     logger.info(f'{n=},{r=},{eq=},{linha=}')
#     logger.info(f'Expressão certa? {r == linha}')
#
#     qtd_portas = conta_quantidade_de_portas(eq)
#     logger.info(f'Quantidade de portas = {qtd_portas}')
#
#     '''
#     for permutacao in permutacoes:
#         executa_aux(permutacao)
#     # '''


if __name__ == '__main__':
    # permutacoes = realiza_leitura('./data/toffoli_fredkin_3bits.json')
    permutacoes = [
        # "('001', '000', '101', '010', '111', '110', '011', '100')",
        # "('00', '01', '10', '11')",
        "('0000', '1101', '1111', '1000', '0110', '0001', '1010', '1100', '0011', '1011', '1110', '0111', '0100', '0101', '0010', '1001')",
    ]

    # sanitiza as permutações lidas/informadas
    permutacoes = [sanitiza_permutacao(perm) for perm in permutacoes]

    # executa o reed-muller
    # executa(permutacoes, debug=1)
