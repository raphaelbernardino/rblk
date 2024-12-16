from math import log2

import numpy as np

from novo.circuitos.alvo import Alvo
from novo.circuitos.circuito import Circuito
from novo.circuitos.controle import Controle
from novo.circuitos.toffoli import Toffoli
from novo.logs.logging_utils import create_logger

logger = create_logger(name='util_reed', level='DEBUG')


def gera_porta_circuito(expressao, alvo, prefixo='b', valor_inicial=0):
    logger.debug(f'=======> {expressao=}')
    partes = expressao.split('&')
    partes = [parte.strip().replace(' ', '') for parte in partes]
    logger.debug(f'{len(partes)=} :: {partes=}')

    alvos = list()

    if type(alvo) is int:
        alvos = Alvo(alvo)
    else:
        for a in alvo:
            um_alvo = Alvo(a)
            alvos.append(um_alvo)

    logger.debug(f'Alvo(s): {alvos}')

    # constroi os controles
    controles = list()

    for parte in partes:
        ctrl_linha_str = parte.replace(prefixo, '')
        ctrl_sinal = True

        if parte.startswith('~'):
            ctrl_linha_str = parte[1 + len(prefixo):]
            ctrl_sinal = False

        if ctrl_linha_str != '':
            logger.debug(f'{ctrl_linha_str=}')
            ctrl_linha = int(ctrl_linha_str)
            ctrl = Controle(ctrl_linha, ctrl_sinal)
            controles.append(ctrl)

    logger.debug(f'Controle(s): {controles}')

    # alvos = list()
    # controles = list()
    #
    # if len(partes) == 1:
    #     parte = partes[0]
    #
    #     alvo_str = parte[0 + len(prefixo):]
    #     if parte.startswith('~'):
    #         alvo_str = parte[1 + len(prefixo):]
    #     # logger.info(f'{alvo_str=}')
    #
    #     linha_alvo = int(alvo_str)
    #     alvo = Alvo(linha_alvo)
    #     # logger.info(f'{type(alvo)} {alvo=}')
    #     alvos.append(alvo)
    #
    # elif len(partes) > 1:
    #     parte = partes[0]
    #
    #     alvo_str = parte[0 + len(prefixo):]
    #     if parte.startswith('~'):
    #         alvo_str = parte[1 + len(prefixo):]
    #
    #     linha_alvo = int(alvo_str)
    #     alvo = Alvo(linha_alvo)
    #     # logger.info(f'{type(alvo)} {alvo=}')
    #
    #     alvos.append(alvo)
    #
    #     for parte in partes[1:]:
    #         logger.info(f'{parte=}')
    #         ctrl_linha_str = parte[0 + len(prefixo):]
    #         ctrl_sinal = True
    #         if parte.startswith('~'):
    #             ctrl_linha_str = parte[1 + len(prefixo):]
    #             ctrl_sinal = False
    #
    #         ctrl_linha = int(ctrl_linha_str)
    #         ctrl = Controle(ctrl_linha, ctrl_sinal)
    #         # logger.info(f'{type(ctrl)} {ctrl=}')
    #
    #         controles.append(ctrl)

    # if len(alvos) == 1:
    #     porta = Toffoli(alvos, controles)
    # elif len(alvos) == 2:
    #     porta = Fredkin(alvos, controles)

    porta = Toffoli(alvos, controles)
    return porta


def reduz_representacao_portas(portas):
    identificador_de_not = '1'

    if identificador_de_not in portas:
        # qual a quantidade de negacoes na expressao?
        qtd = portas.count(identificador_de_not)

        # se for par, é só remover
        for _ in range(qtd):
            portas.remove(identificador_de_not)

        # caso seja impar, adiciona uma negacao na frente
        if qtd % 2 == 1:
            portas[0] = '~' + portas[0]

    # return portas


def gera_circuito(expressao, alvo, ancillas, qtd_vars, prefixo='b'):
    logger.debug(f'**************> {expressao=}')
    if expressao.strip() == '':
        return Circuito(qtd_vars=qtd_vars, ancillas=ancillas)

    portas = extrai_portas(expressao, alvo)

    portas_circuito = list()
    for p in portas:
        porta_circuito = gera_porta_circuito(p, alvo, prefixo=prefixo)
        portas_circuito.append(porta_circuito)

    logger.debug(f'Portas: {portas_circuito=} :: Qtd. vars: {qtd_vars=}')
    return Circuito(portas_circuito, qtd_vars, ancillas=ancillas)


def extrai_portas(expressao, alvo):
    # reduz espaços da expressão
    expressao = ' '.join(expressao.split())
    logger.debug(f'Expr: {expressao}')

    ####
    # expressao1 = 'b0 ^ b1 & b2 ^ b3'
    # expressao2 = 'b0 ^ b1 ^ b2 ^ b3'
    # expressao3 = '1'
    ####

    portas = list()

    if expressao == '1':
        # return [f'~b{alvo}']
        porta = ''
        portas.append(porta)
        return portas

    portas = expressao.split('^')
    portas = [porta.strip() for porta in portas]
    reduz_representacao_portas(portas)
    logger.debug(f'Portas: {portas}')

    # temp = expressao.split('^')
    # temp = [t.strip() for t in temp]
    # i = 0
    #
    # temp2 = list()
    # while i < len(temp):
    #     temp2.append(temp[i])
    #
    #     if '&' in temp[i]:
    #         porta = '^'.join(temp2)
    #         portas.append(porta)
    #         temp2 = list()
    #
    #     i += 1
    #
    # if len(temp2) > 0:
    #     porta = '^'.join(temp2)
    #     portas.append(porta)

    # portas = list()
    # i = 0
    # while i < len(expressao):
    #     porta = ''
    #
    #     # junta as partes
    #     while porta.count('^') < 2 and i < len(expressao):
    #         porta = porta + expressao[i]
    #         i += 1
    #         # logger.info(f'P = {porta}')
    #
    #     portas.append(porta)
    #     i += 1
    # logger.debug(f'Portas = {portas}')

    return portas


# def gera_arquivo_tfc(expressao, nome_do_arquivo):
#     circuito = gera_circuito(expressao)
#     circuito.salva_em_arquivo(nome_do_arquivo)


def determina_quantidades_de_bits(d):
    return int(log2(len(d)))


def extrai_linhas(p):
    """
        ['000', '001', '010', '011', '100', '101', '110', '111']

        ==>

        [   ['0', '0', '0', '0', '1', '1', '1', '1'],
            ['0', '0', '1', '1', '0', '0', '1', '1'],
            ['0', '1', '0', '1', '0', '1', '0', '1']
        ]
    """

    # convertendo cada conjunto de N bits numa posição do vetor
    v = [list(k) for k in p]

    # calculando a transposta dos conjuntos de N bits
    v_as_np = np.array(v, dtype=int)
    t = v_as_np.transpose()

    # retorna (passo-a-passo) a linha completa da permutação
    for linha in t:
        linha_permutacao = list(linha)
        yield linha_permutacao


def sanitiza_permutacao(p):
    """
        "('000', '001', '010', '011', '100', '101', '110', '111')"

        ==>

        ['000', '001', '010', '011', '100', '101', '110', '111']
    """
    s = p.strip()

    s = s.replace('(', '')
    s = s.replace(')', '')

    s = s.replace("'", '')

    ps = [k.strip() for k in s.split(',')]

    return ps


def transforma_saida_funcao(f):
    """
    In the S coding, the {0, 1} values corresponding to true and false minterms are
    respectively replaced by the {1, −1} values.
    """

    g = list()
    t = {0: 1, 1: -1}

    for i in f:
        e = t.get(i)

        if e:
            g.append(e)
        else:
            raise Exception("The function contains errors. The output must contain only 0's and 1's")

    return np.array(g, dtype=np.int8)


def multiplica_matrizes(h, f):
    """
    add @measure to test performance on this function.

    Function Name       : multiplica_matrizes (with matmul)
    Elapsed time        :     0.0189 msecs
    Current memory usage:     0.0006 MB
    Peak                :     0.0009 MB

    Function Name       : multiplica_matrizes (with dot)
    Elapsed time        :     0.0285 msecs
    Current memory usage:     0.0015 MB
    Peak                :     0.0068 MB
    """

    s = np.matmul(h, f)
    return s


def gera_matriz_walsh_hadamard(n):
    """
    Walsh functions can be generated in a recursive way by using the Hadamard
    matrix (Hurst et al., 1985).

    Tw(0) = [1]
    Tw(n) = [ [Tw(n - 1), Tw(n - 1)], [Tw(n - 1), -Tw(n - 1)] ]
    """

    h0 = np.array([[1, 1], [1, -1]], dtype=np.int8)
    h = h0
    while len(h) < n:
        h = np.kron(h, h0)

    return h


def aplica_funcao_s(coef):
    """
    000 --> 0 -->
    001 --> 1 --> x3
    010 --> 2 --> x2
    100 --> 3 --> x1
    ...
    111 --> 7 --> x1x2x3
    """

    coef = list(coef)
    n = int(log2(len(coef)))

    valor, pos = identifica_maior_magnitude(coef)
    r = f'{pos:b}'.zfill(n)
    logger.debug(f'maior magnitude = {valor} :: indice = {pos} ==> {r}')

    negado = False
    if valor < 0:
        negado = True

    # [f'x{j+1}' if x == '1' else '' for j, x in enumerate('111')]

    linhas = list()
    for i in range(len(coef)):
        str_linha = f'{i:b}'.zfill(n)
        linha = list(str_linha)
        # logger.debug(f'antes == {linha=}', end='\t')

        for j, x in enumerate(r):
            if x == '1':
                if negado:
                    linha[j] = '0' if linha[j] == '1' else '1'

        # logger.debug(f'depois == {linha=}')
        linhas.append(linha)

    saida = list()
    for linha in linhas:
        t = list()

        for j, x in enumerate(r):
            if x == '1':
                k = int(linha[j])
                t.append(k)

        # logger.debug(f'T antes  > {t}')
        t = reduz_linha_xor(t)
        # logger.debug(f'T depois > {t}')
        saida.append(t)

    return saida


def reduz_linha_xor(lin):
    """
    x1 ^ x2 ==> x1 XOR x2
    """
    if len(lin) < 1:
        return 0
    ll = [str(x) for x in lin]
    tt = '^'.join(ll)
    res = eval(tt)
    return res


def reduz_linha_and(lin):
    """
    x1 x2 ==> x1 AND x2 ==> x1 * x2
    """

    return np.prod(lin)


def concordancia_de_funcoes(f1, f2):
    """
    Compute the function d(x) = f (x) ⊕ fs (x). The function d(x) indicates the number of
    agreements (disagreements) between f (x) and fs (x) at point x:

    d(x) = 1 for f(x) != fs(x).
    d(x) = 0 for f(x) == fs(x).
    """

    d = list()

    if len(f1) != len(f2):
        raise Exception("The function contains errors. Functions should have the same length.")

    for i in range(len(f1)):
        x1 = f1[i]
        x2 = f2[i]

        r = 1 if x1 != x2 else 0

        d.append(r)

    return d


def identifica_maior_magnitude(coeficiente_espectral):
    """
    We find coefficients with the largest magnitudes. In our example this condition is satisfied
    for the coefficient s1 = −6. Hence, f(x) = f(x3).

    Example: [2, −6, 2, 2, −2, −2, −2, −2]
    """

    magnitudes = coeficiente_espectral[:]
    magnitudes.sort(key=abs, reverse=True)

    maior_magnitude = magnitudes[0]
    posicao = coeficiente_espectral.index(maior_magnitude)

    return maior_magnitude, posicao


def gera_string_binaria_equivalente(s, estados, n, gerar_negativos=False, alvo=0):
    variaveis = list()

    # gera uma representacao binaria do indice do espectro de reed muller
    r = f'{s:b}'.zfill(n)
    logger.debug(f'Indice Maior Magnitude RM: {s}, Lista de Estados: {estados}, Qtd. Bits: {n}')

    for j, x in enumerate(r):
        if x == '1':
            k = f'{estados[j]}'
            variaveis.append(k)
        elif gerar_negativos and x == '0':
            k = f'~{estados[j]}'
            variaveis.append(k)

    return variaveis


def gera_equacao_d(coef, estados, simbolo_xor='⊕', alvo=0):
    n = int(log2(len(coef)))
    coef = list(coef)
    variaveis = list()

    valor, pos = identifica_maior_magnitude(coef)
    eq = ''

    variaveis += gera_string_binaria_equivalente(pos, estados, n, gerar_negativos=False, alvo=alvo)
    logger.debug(f'{variaveis=}')

    if len(variaveis) > 0 and valor < 0:
        variaveis.append('1')

    if '1' in variaveis:
        variaveis2 = list()

        for v in variaveis:
            if v != '1':
                v = f'~{v}'
                variaveis2.append(v)

        variaveis = variaveis2

    eq += f' {simbolo_xor} '.join(variaveis)
    # eq += f' {simbolo_xor} '

    logger.debug(f'variaveis ==> {variaveis}')
    logger.debug(f'eq ==> {eq}')

    return eq.strip(f' {simbolo_xor} ')


def executa_linha(f0, estados, nivel, alvo=0):
    f1 = transforma_saida_funcao(f0)
    # espacos = '   ' * nivel
    logger.debug(f'Transformando :: F{nivel} = {f0} ==> F{nivel}\' = {f1}')

    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.hadamard.html
    n = len(f0)
    wh = gera_matriz_walsh_hadamard(n)
    # logger.debug(f'WH = {wh}')

    s = multiplica_matrizes(wh, f1)
    logger.debug(f'S  = {s}')

    fn = aplica_funcao_s(s)
    logger.debug(f'Fn = {fn}')

    d = concordancia_de_funcoes(f0, fn)
    logger.debug(f'DH = {d}')

    r0 = d.count(0)
    r1 = d.count(1)
    r = min(r0, r1) / len(fn)
    logger.debug(f'R  = {r}')

    eq_d = gera_equacao_d(s, estados, alvo=alvo)
    # logger.debug(f'EQ = {eq_d}')

    return r, eq_d, d
