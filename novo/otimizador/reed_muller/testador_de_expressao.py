import re
from itertools import product

from rich.traceback import install

from novo.logs.logging_utils import create_logger

install(show_locals=True)

logger = create_logger('testador', level='INFO')

XOR = '⊕'
AND = '.'
VAZIO = 'Ø'


def substitui_simbolos(expressao):
    expressao = expressao.replace(AND, '&')
    expressao = expressao.replace(XOR, '^')
    expressao = expressao.replace(VAZIO, '')

    # inclui '~' das variaveis
    # expressao = 'b1 ^ 1' ==> '~b1'
    regex = r'[a-zA-Z]+[0-9]+\s+\^\s+1'
    variaveis = re.findall(regex, expressao)
    for s in variaveis:
        tt = s.replace(' ^ 1', '')
        tt = '~' + tt
        expressao = expressao.replace(s, tt)

    # sanitiza expressão
    expressao = ' ' + expressao.strip(' ') + ' '
    while '  ' in expressao:
        expressao = expressao.replace('  ', ' ')

    return expressao


def extrai_variaveis(expressao, estados):
    if estados:
        return sorted(estados)

    # encontra todas as variaveis
    regex = r'[\~a-zA-Z]+[0-9]+'
    variaveis = re.findall(regex, expressao)

    # remove '~' das variaveis
    variaveis = [s.replace('~', '') for s in variaveis]

    # reduz o tamanho da lista de variaveis
    variaveis = set(variaveis)

    return sorted(variaveis)


def gera_tabela_verdade(nbits):
    for linha in product([0, 1], repeat=nbits):
        yield list(linha)


def preenche_faltantes(variaveis, qtd, identificador='x'):
    for i in range(1, qtd):
        var = f'{identificador}{i}'
        if var not in variaveis:
            variaveis.append(var)


def cria_mapeamento_de_simbolos(expressao, identificador='x', nbits=None, estados=None):
    # extrai as variaveis da expressao dada
    variaveis = extrai_variaveis(expressao, estados)
    logger.debug(f'VARRR {variaveis}')

    if nbits is None:
        # quantos bits são necessários?
        nbits = len(variaveis)
        logger.debug(f'Expressão avaliada usando {nbits} bits')

    elif len(variaveis) != nbits:
        logger.debug(f'AAAAAA {variaveis} ===== {nbits}')
        # se a quantidade de variaveis é diferente da quantidade de bits desejada
        preenche_faltantes(variaveis, nbits, identificador)

    # ordena as variaveis para fins de organização
    variaveis = sorted(variaveis)
    logger.debug(f'vars {variaveis}')

    # cria os mapeamentos
    mapeamentos = dict()

    for linha in gera_tabela_verdade(nbits):
        for pos, var in enumerate(variaveis):
            mapeamentos[f'{var}'] = linha[pos]
            mapeamentos[f'~{var}'] = 0 if linha[pos] else 1

        yield mapeamentos


def avalia(expressao, identificador='x', nbits=None, estados=None):
    resultados = list()

    for mapeamento in cria_mapeamento_de_simbolos(expressao, identificador, nbits, estados):
        logger.debug(f'AVALIA_EXPR MAP :: {mapeamento}')

        # faz uma cópia da expressão original
        expr = expressao[:]
        # logger.debug(f'Antes  :: {expr}\n')

        for var in mapeamento:
            # logger.debug(f'   {var} \t {mapeamento[var]}')
            expr = expr.replace(f' {var} ', f' {mapeamento[var]} ')

        # logger.debug(f'Depois :: {expr}\n')

        expr = expr.strip()
        if expr == '':
            resultado = 0
        else:
            resultado = eval(expr)
        # logger.debug(f'R:: {resultado}\n')

        resultados.append(resultado)

        # logger.debug('-----\n')

    return resultados


def avalia_expressao(expr, identificador='b', nbits=None, estados=None):
    expressao = substitui_simbolos(expr)
    logger.debug(f'== AVALIA_EXPR_IN  ==> {expressao}')

    resultado = avalia(expressao, identificador, nbits, estados)
    logger.debug(f'== AVALIA_EXPR_OUT ==> {resultado}')

    return resultado


if __name__ == '__main__':
    # expr = ' x1 . ( x2 . ( x3 . (Ø) ⊕ ~x3 . (Ø) ⊕ 1) ⊕ ~x2 . ( x3 . (Ø) ⊕ ~x3 . (Ø) ⊕ x3 ) ⊕ ~x2 . ~x3 ⊕ ~x2 . x3 ⊕ x2 . x3 ) ⊕ ~x1 . ( x2 . ( x3 . (Ø) ⊕ ~x3 . (Ø) ⊕ 1) ⊕ ~x2 . ( x3 . (Ø) ⊕ ~x3 . (Ø) ⊕ x3 ) ⊕ ~x2 . ~x3 ⊕ ~x2 . x3 ⊕ x2 . x3 ) ⊕ x1 ⊕ ~x1 . x2 . ~x3 ⊕ x1 . x2 . ~x3'
    # expr = ' ~x1 . ( Ø ) ⊕  x1 . ( Ø ) ⊕ 1 ⊕ x3 '
    # expr = '~x2 . ( ~x1 . ( 1 ) ⊕  x1 . ( 1 ⊕ x3 ) ⊕ ~x1 . ~x3 ⊕ ~x1 . x3 ⊕ x1 . ~x3 ) ⊕  x2 . ( ~x1 . ( 1 ) ⊕  x1 . ( 1 ⊕ x3 ) ⊕ ~x1 . ~x3 ⊕ ~x1 . x3 ⊕ x1 . ~x3 ) ⊕ x2 ⊕ ~x2 . x1 . x3 ⊕ x2 . x1 . x3'
    # expr = '~x2 . ( ~x1 . 1 ⊕  x1 . ( 1 ⊕ x3 ) ⊕ ~x1 . ~x3 ⊕ ~x1 . x3 ⊕ x1 . ~x3 ) ⊕  x2 . ( ~x1 . 1 ⊕  x1 . ( 1 ⊕ x3 ) ⊕ ~x1 . ~x3 ⊕ ~x1 . x3 ⊕ x1 . ~x3 ) ⊕ x2 ⊕ ~x2 . x1 . x3 ⊕ x2 . x1 . x3'
    # expr = '~x2 . ~x3 . x4'

    # expr = 'x3 ⊕ ~x1 . ~x2 . ~x3 . x4 ⊕ x1 . x2 ⊕ x1 . x4 ⊕ x1 . ~x2 . x4 ⊕ x1 . x2 . x3 . ~x4'
    # expr = 'x2 ⊕ x4 ⊕ ~x2 . x4 ⊕ x2 . x3 . ~x4'

    # expr = 'x3 ⊕ ~x1 . ( ~x2 . ~x3 . x4 ⊕ ~x2 . ( ~x3 . x4 ⊕ ~x3 . ( x4 ) ) ) ⊕  x1 . ( x2 ⊕ x4 ⊕  x2 . ( ~x3 . ~x4 ⊕ ~x3 . ( ~x4 ) ) )'
    # expr = 'x3 ⊕ ~x1 . ~x2 . ~x3 . x4 ⊕ x1 . x2 ⊕ x1 . x4'
    # expr = '~x3 . x4'
    # expr = '~b1 & b3 & b4 & b5 ^ ~b1 & b2 & b3 & ~b5 ^ ~b1 & b2 & b3 & b4'

    expr = ' x0 ⊕ x1 ⊕ 1 ⊕  ~x0  ⊕  x0 '

    r = avalia_expressao(expr, identificador='x')
    logger.info(r)
