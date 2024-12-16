from itertools import product

import pytest

from novo.otimizador.reed_muller.reed_recursivo import gera_estados, processa_permutacao
from novo.otimizador.reed_muller.testador_de_expressao import avalia_expressao


def gen_tbl_bits(n):
    return product([0, 1], repeat=2 ** n)


def check_nbits(n, sequence, alvo=0):
    linha = list(sequence)
    print(f'Linha = {linha}')

    alvos = [alvo]
    print(f'Alvos = {alvos}')

    estados = gera_estados(n, alvos)
    # estados = gera_estados(n)
    eq = processa_permutacao(linha, n, estados, alvo=alvo)
    r = avalia_expressao(eq, identificador='x', nbits=n, estados=estados)

    return linha, r


# all_n = range(1, 7)
# @pytest.mark.parametrize("n", all_n)
# def test_all_bits(n):
#     print(f'{n=}')
#
#     for sequence in gen_tbl_bits(n):
#         linha, r = check_nbits(n, sequence)
#         assert linha == r


tbl_1bits = gen_tbl_bits(1)
tbl_2bits = gen_tbl_bits(2)
tbl_3bits = gen_tbl_bits(3)
tbl_4bits = gen_tbl_bits(4)


# tbl_5bits = gen_tbl_bits(5)
# tbl_6bits = gen_tbl_bits(6)


@pytest.mark.parametrize("sequence", tbl_1bits)
def test_1bits(sequence):
    n = 1
    linha, r = check_nbits(n, sequence)
    assert linha == r


@pytest.mark.parametrize("sequence", tbl_2bits)
def test_2bits(sequence):
    n = 2
    linha, r = check_nbits(n, sequence)
    assert linha == r


@pytest.mark.parametrize("sequence", tbl_3bits)
def test_3bits(sequence):
    n = 3
    linha, r = check_nbits(n, sequence)
    assert linha == r


@pytest.mark.parametrize("sequence", tbl_4bits)
def test_4bits(sequence):
    n = 4
    linha, r = check_nbits(n, sequence)
    assert linha == r


if __name__ == '__main__':
    pytest.main()
