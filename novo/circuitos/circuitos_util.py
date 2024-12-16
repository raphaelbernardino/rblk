from itertools import product


def gera_tabela_verdade(qtd_bits, ancillas=0):
    for linha in product([0, 1], repeat=qtd_bits):
        temp = list(linha)
        temp += [0] * ancillas
        yield temp


def gera_permutacao(qtd_bits):
    n = 2 ** qtd_bits
    estado = list()
    # estado = np.empty(n, dtype='object')

    for i in range(n):
        k = bin(i)[2:].zfill(qtd_bits)
        estado.append(k)
        # estado[i] = bin(i)[2:].zfill(qtd_bits)

    return estado


def inverte_elementos(elementos):
    for i in range(len(elementos)):
        elementos[i] = elementos[i][::-1]
