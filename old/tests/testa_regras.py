from itertools import product

import pytest

from novo.circuitos.circuito import Circuito
from novo.gerador.gerador_de_circuitos import define_portas_toffoli
from novo.otimizador.otimizador_util import realiza_leitura_tfc
from novo.regras.regra1 import aplica_eliminacao_de_portas_iguais
from novo.regras.regra2 import aplica_eliminacao_de_not_duplicado
from novo.regras.regra3 import aplica_merge
from novo.regras.regra4 import aplica_swap_no_circuito
from novo.regras.regra5 import aplica_move_no_circuito

# https://giovannireisnunes.wordpress.com/2018/11/30/cobertura-de-codigo-com-pytest/

# CONFIG. BRUTE FORCE
SKIP_BRUTE = True
QTD_BITS = 3
QTD_PORTAS = 6
#####################


def gera_circuitos_parciais_para_teste(qtd_bits, qtd_portas):
    f"""
    Gera os circuitos de {qtd_bits} bits e usando, no máximo, {qtd_portas} portas.
    
    @param qtd_bits: A quantidade de bits que cada circuito utilizará.
    @param qtd_portas: A quantidade máxima de portas que cada circuito possui.
    @return: Um circuito de {qtd_bits} bits e quantidade de portas entre 1 e {qtd_portas}.
    """
    # define as portas que serão utilizadas
    portas = define_portas_toffoli(qtd_bits)

    # gera os circuitos usando de 1 porta até {qtd_portas} portas
    for i in range(1, qtd_portas + 1):
        # realiza a combinação das portas entre si, limitando ao tamanho de portas
        for circ in product(portas, repeat=i):
            # cria o circuito a partir da combinação gerada
            circuito = Circuito(circ, qtd_bits)

            # retorna o circuito criado
            yield circuito


def gera_circuitos_para_teste(qtd_bits, qtd_portas):
    f"""
    Gera todos os circuitos de {qtd_bits} bits contendo até {qtd_portas} portas.
    
    @param qtd_bits: Quantidade máxima de bits por circuito.
    @param qtd_portas: Quantidade máxima de portas por circuito.
    @return: Todos os circuitos contendo entre 1 e {qtd_bits} bits, e de 1 porta até {qtd_portas} portas.
    """
    # gera os circuitos de 1 a {qtd_bits} bits
    for n in range(1, qtd_bits + 1):
        # gera parcialmente os circuitos de N bits contendo até {qtd_portas} portas
        for circuito in gera_circuitos_parciais_para_teste(n, qtd_portas):
            yield circuito


def aplica_regra(circuito, regra):
    print(f'=== Circuito Original\n{circuito}')

    # extrai a permutacao a partir do circuito
    permutacao_original = circuito.obtem_permutacao()

    # tenta aplicar a regra
    regra(circuito)

    print(f'\n=== Circuito Otimizado\n{circuito}')
    permutacao_apos_regra = circuito.obtem_permutacao()

    assert permutacao_original == permutacao_apos_regra


###### Testes fixos usando arquivos ######
@pytest.mark.parametrize("arquivo", [
    './tests/arquivos_de_teste_para_regras/regra1_teste01.tfc',
])
def testa_regra1_arquivos(arquivo):
    circ = realiza_leitura_tfc(arquivo)
    aplica_regra(circ, aplica_eliminacao_de_portas_iguais)


@pytest.mark.parametrize("arquivo", [
    './tests/arquivos_de_teste_para_regras/regra2_teste01.tfc',
    './tests/arquivos_de_teste_para_regras/regra2_teste02.tfc',
    './tests/arquivos_de_teste_para_regras/regra2_teste03.tfc',
])
def testa_regra2_arquivos(arquivo):
    circ = realiza_leitura_tfc(arquivo)
    aplica_regra(circ, aplica_eliminacao_de_not_duplicado)


@pytest.mark.parametrize("arquivo", [
    './tests/arquivos_de_teste_para_regras/regra3_teste01.tfc',
    './tests/arquivos_de_teste_para_regras/regra3_teste02.tfc',
    './tests/arquivos_de_teste_para_regras/regra3_teste03.tfc',
])
def testa_regra3_arquivos(arquivo):
    circ = realiza_leitura_tfc(arquivo)
    aplica_regra(circ, aplica_merge)


@pytest.mark.parametrize("arquivo", [
    './tests/arquivos_de_teste_para_regras/regra4_teste01.tfc',
    './tests/arquivos_de_teste_para_regras/regra4_teste02.tfc',
    './tests/arquivos_de_teste_para_regras/regra4_teste03.tfc',
    './tests/arquivos_de_teste_para_regras/regra4_teste04.tfc',
])
def testa_regra4_arquivos(arquivo):
    circ = realiza_leitura_tfc(arquivo)
    aplica_regra(circ, aplica_swap_no_circuito)


@pytest.mark.parametrize("arquivo", [
    './tests/arquivos_de_teste_para_regras/regra5_teste01.tfc',
])
def testa_regra5_arquivos(arquivo):
    circ = realiza_leitura_tfc(arquivo)
    aplica_regra(circ, aplica_move_no_circuito)


###### Testes de força bruta ######
@pytest.mark.skipif(SKIP_BRUTE, reason="Skipping brute force test.")
def testa_regra1():
    """
    Testa a Regra 1 -- eliminação de portas duplicadas.
    """

    for circ in gera_circuitos_para_teste(qtd_bits=QTD_BITS, qtd_portas=QTD_PORTAS):
        print(type(circ), circ)
        aplica_regra(circuito=circ, regra=aplica_eliminacao_de_portas_iguais)


@pytest.mark.skipif(SKIP_BRUTE, reason="Skipping brute force test.")
def testa_regra2():
    """
    Testa a Regra 2 -- eliminação de NOTs.
    """

    for circ in gera_circuitos_para_teste(qtd_bits=QTD_BITS, qtd_portas=QTD_PORTAS):
        aplica_regra(circuito=circ, regra=aplica_eliminacao_de_not_duplicado)


@pytest.mark.skipif(SKIP_BRUTE, reason="Skipping brute force test.")
def testa_regra3():
    """
    Testa a Regra 3 -- fusão de portas adjacentes.
    """

    for circ in gera_circuitos_para_teste(qtd_bits=QTD_BITS, qtd_portas=QTD_PORTAS):
        aplica_regra(circuito=circ, regra=aplica_merge)


@pytest.mark.skipif(SKIP_BRUTE, reason="Skipping brute force test.")
def testa_regra4():
    """
    Testa a Regra 4 -- comutação.
    """

    for circ in gera_circuitos_para_teste(qtd_bits=QTD_BITS, qtd_portas=QTD_PORTAS):
        aplica_regra(circuito=circ, regra=aplica_swap_no_circuito)


@pytest.mark.skipif(SKIP_BRUTE, reason="Skipping brute force test.")
def testa_regra5():
    """
    Testa a Regra 5 -- movimentação.
    """

    for circ in gera_circuitos_para_teste(qtd_bits=QTD_BITS, qtd_portas=QTD_PORTAS):
        aplica_regra(circuito=circ, regra=aplica_move_no_circuito)


if __name__ == '__main__':
    print('Iniciando testes...\n')

    # circ = realiza_leitura_tfc('./testes/template4_teste01.tfc')
    # testa_aplicacao_de_regra(circ, pode_realizar_template4)
    # pg, ph = circ.portas
    # complementa_portas(pg, ph)
