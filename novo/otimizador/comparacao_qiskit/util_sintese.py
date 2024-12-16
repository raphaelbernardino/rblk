import random
import re
from itertools import product
from pathlib import Path

import numpy as np
# https://docs.quantum.ibm.com/
import qiskit.quantum_info as qi
from qiskit import transpile, QuantumCircuit
from qiskit.qasm3 import dumps

from novo.circuitos.alvo import Alvo
from novo.circuitos.circuito import Circuito
from novo.circuitos.controle import Controle
from novo.circuitos.states import States
from novo.circuitos.toffoli import Toffoli
from novo.logs.logging_utils import create_logger

logger = create_logger(name='util_sintese', level='INFO')


def traduz_portas_do_circuito(circuito, portas=('cx', 'ccx', 'u3')):
    """
    Representa o circuito/operador original usando as portas informadas
    """
    transpiled = transpile(circuito, basis_gates=portas)

    return transpiled


def salva_circuito(circuito, nome_circuito='circuito.png'):
    # cria representação gráfica do circuito
    desenho_circuito = circuito.draw('mpl')

    # cria destino
    destino = Path('./images/', nome_circuito)
    destino.parent.mkdir(exist_ok=True, parents=True)

    # salva desenho do circuito no destino
    desenho_circuito.savefig(destino)
    logger.info(f'Circuito salvo em: {destino}')


# https://quantumcomputing.stackexchange.com/a/38575
def obtem_qasm(circuito_quantico):
    qasm_str = dumps(circuito_quantico)
    return qasm_str.strip()


def converte_qasm_em_circuito(qasm):
    if not isinstance(qasm, str):
        raise Exception('A entrada QASM deve ser do tipo string.')

    # define o regex para extrair as variaveis
    regex = re.compile(r'\d+')

    # define a quantidade de variaveis e a lista de portas inicial
    qtd_vars = 0
    portas = list()

    for linha in qasm.split('\n'):
        logger.debug(f'Linha: {linha}')

        if linha.startswith('qubit'):
            temp = re.findall(regex, linha)
            qtd_vars = int(temp[0])
            logger.debug(f'qtd_vars: {qtd_vars}')

        if linha.startswith('cx'):
            temp = re.findall(regex, linha)
            linha_alvo = temp[0]
            linhas_controles = temp[1:]
            logger.debug(f'L == Alvo: {linha_alvo} :: Controles: {linhas_controles}')

            # constroi o alvo
            um_alvo = Alvo(linha_alvo)

            # constroi os controles
            controles = list()
            for ctrl in linhas_controles:
                linha_controle = int(ctrl)
                um_controle = Controle(linha_controle, States.ctrl_positivo)
                controles.append(um_controle)

            logger.debug(f'K == Alvo: {um_alvo} :: Controles: {controles}')

            # cria a porta usando alvo e controles
            uma_porta = Toffoli(alvos=[um_alvo], controles=controles)

            # adiciona a porta criada na lista de portas
            portas.append(uma_porta)

    # cria o circuito final usando a lista de portas
    circ = Circuito(portas=portas, qtd_vars=qtd_vars, ancillas=0)

    return circ


def cria_operador_qiskit(matriz):
    """
    Cria um operador a partir da matriz informada

    https://docs.quantum.ibm.com/api/qiskit/qiskit.quantum_info.Operator
    """
    generic_operator = qi.Operator(matriz)
    return generic_operator


def cria_circuito_quantico(operador, qbits=2, nome_circuito='QGate'):
    """
    Recebe um operador do QisKit e retorna um circuito

    Unitary
    https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.library.UnitaryGate
    """
    qc = QuantumCircuit(qbits)
    qc.unitary(operador, range(qbits), label=nome_circuito)

    return qc


def obtem_representacao_binaria_da_linha(lin):
    representacao_binaria = ''
    for j in range(len(lin)):
        representacao_binaria += str(lin[j])
    return representacao_binaria


def converte_permutacao_em_matriz(perm, n):
    if not isinstance(perm[0], str):
        raise Exception('Utilize uma permutação, e não a tabela verdade.')

    if len(set(perm)) != len(perm):
        logger.error('A matriz gerada não será unitária.')

    # cria uma matriz de zeros com dimensao 2^n x 2^n (usando um 8 bits por espaço)
    k = 2 ** n
    matriz = np.zeros(shape=(k, k), dtype=np.uint8)

    for i in range(len(perm)):
        r = int(perm[i], 2)
        # logger.debug(f'Tradução de binário para inteiro --> {r}')

        matriz[i, r] = 1

    # logger.debug(f'Matriz de permutação:\n{matriz}')
    return matriz


def converte_permutacao_em_tabela_verdade(permutacao):
    if not isinstance(permutacao[0], str):
        raise Exception('Utilize uma permutação, e não a tabela verdade.')

    return [list(map(int, list(p))) for p in permutacao]


def converte_tabela_verdade_em_permutacao(tbl):
    if not (isinstance(tbl[0], list) or isinstance(tbl[0], np.ndarray)):
        logger.info(f'{type(tbl[0])}')
        raise Exception('Utilize uma tabela verdade, e não uma permutação.')

    permutacao = list()

    for i in range(len(tbl)):
        b = obtem_representacao_binaria_da_linha(tbl[i])
        logger.debug(f'Representação binária da linha #{i} --> {b}')

        permutacao.append(b)

    logger.debug(f'Permutação:\n{permutacao}')
    return permutacao


# https://quantumcomputing.stackexchange.com/a/29601
def gera_matriz_de_permutacao(dados, n):
    if isinstance(dados[0], list):
        dados = converte_tabela_verdade_em_permutacao(dados)

    if not isinstance(dados[0], str):
        raise Exception('Verifique os dados de entrada. A entrada deve ser uma permutação ou uma tabela verdade.')

    # obtem a matriz de permutacao associada
    matriz = converte_permutacao_em_matriz(dados, n)

    return matriz


# def iter_sample_dist_naive(iterable, samplesize, chunksize=10000):
#     samples = []
#     it = iter(iterable)
#
#     try:
#         while True:
#             first = next(it)
#             chunk = chain([first], islice(it, chunksize - 1))
#             samples += random.sample(list(chunk), samplesize)
#
#     except StopIteration:
#         return random.sample(samples, samplesize)


def gera_permutacao_aleatoria(n):
    # cria uma permutacao de N bits
    permutacao = [''.join(p) for p in product('01', repeat=n)]
    # permutacao = [f'{bin(i)[2:].zfill(n)}' for i in range(2 ** n)]

    # randomiza os dados
    random.shuffle(permutacao)

    return permutacao
