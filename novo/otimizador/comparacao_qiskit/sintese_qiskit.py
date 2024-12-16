import math
import random

# https://docs.quantum.ibm.com/
from qiskit.synthesis import synth_cnot_count_full_pmh, synth_permutation_depth_lnn_kms, synth_permutation_basic, \
    synth_permutation_acg

from novo.logs.logging_utils import create_logger
from novo.otimizador.comparacao_qiskit.util_sintese import cria_operador_qiskit, cria_circuito_quantico, \
    traduz_portas_do_circuito, converte_tabela_verdade_em_permutacao, gera_permutacao_aleatoria, \
    converte_permutacao_em_tabela_verdade, gera_matriz_de_permutacao, obtem_qasm, converte_qasm_em_circuito
from novo.otimizador.otimizador_main import executa_regras, executa_reed, executa_otimos
from novo.otimizador.otimizador_reed import executa_sintese
from novo.otimizador.otimizador_util import processa_tfc

logger = create_logger(name='sintese_qiskit', level='INFO')


def cria_circuito_unitario_qsikit(matriz):
    """
    Realiza o processo de sintese usando uma matriz unitária.

    https://github.com/Qiskit/qiskit/blob/main/qiskit/transpiler/passes/synthesis/unitary_synthesis.py
    """
    # cria o operador associado
    operador = cria_operador_qiskit(matriz)

    # define qtd. de qbits
    qbits = math.log2(len(matriz))
    qbits = math.ceil(qbits)

    # cria circuito
    circ = cria_circuito_quantico(operador=operador, qbits=qbits)
    # circ = qs_decomposition(matriz)
    # logger.debug(f'Circuito Original:\n{circ}')

    # traduz circuito usando as portas informadas
    trans_circ = traduz_portas_do_circuito(circ, portas=['u', 'cx', 'ccx'])
    # logger.debug(f'Circuito Traduzido:\n{trans_circ}')

    # # salva o desenho do circuito
    # salva_circuito(trans_circ, nome_circuito='circuito.png')

    return trans_circ


def cria_circuito_linear_qsikit(matriz):
    """
    Realiza o processo de sintese usando uma função linear.

    ----
    Synthesize linear reversible circuits for all-to-all architecture using Patel, Markov and Hayes method.
    Efficient Synthesis of Linear Reversible Circuits, Quantum Information & Computation 8.3 (2008)
    https://arxiv.org/abs/quant-ph/0302002
    ----

    https://docs.quantum.ibm.com/api/qiskit/synthesis#linear-function-synthesis
    https://github.com/Qiskit/qiskit/tree/main/qiskit/synthesis
    """
    # cria circuito
    circ = synth_cnot_count_full_pmh(matriz)
    # logger.debug(f'Circuito Original:\n{circ}')

    # traduz circuito usando as portas informadas
    trans_circ = traduz_portas_do_circuito(circ, portas=['cx', 'ccx'])
    # logger.debug(f'Circuito Traduzido:\n{trans_circ}')

    # # salva o desenho do circuito
    # salva_circuito(trans_circ, nome_circuito='circuito.png')

    return trans_circ


def cria_circuito_permutacao(permutacao, metodo='depth'):
    """
    Realiza o processo de sintese a partir da permutação.

    ----
    depth::
    Synthesize a permutation circuit for a linear nearest-neighbor architecture using the Kutin, Moulton, Smithline method.
    Computation at a distance (2007)
    https://arxiv.org/abs/quant-ph/0701194

    acg::
    Synthesize a permutation circuit for a fully-connected architecture using the Alon, Chung, Graham method.
    Routing permutations on graphs via matchings, Proceedings of the 25th Annual ACM Symposium on Theory of Computing (1993)
    https://doi.org/10.1145/167088.167239
    ----

    https://docs.quantum.ibm.com/api/qiskit/synthesis#permutation-synthesis
    https://github.com/Qiskit/qiskit/tree/main/qiskit/synthesis
    """
    # transforma para permutação, se estiver na forma de tabela verdade
    if not isinstance(permutacao[0], str):
        permutacao = converte_tabela_verdade_em_permutacao(permutacao)

    # converte a permutacao para o padrao qiskit
    perm = [int(i, 2) for i in permutacao]

    # define a funcao a ser utilizada
    funcoes = {
        'acg': synth_permutation_acg,
        'basic': synth_permutation_basic,
        'depth': synth_permutation_depth_lnn_kms,
    }
    funcao = funcoes[metodo]

    # cria circuito
    circ = funcao(perm)
    logger.debug(f'Circuito Original:\n{circ}')

    # traduz circuito usando as portas informadas
    trans_circ = traduz_portas_do_circuito(circ, portas=['cx', 'ccx'])
    # logger.debug(f'Circuito Traduzido:\n{trans_circ}\n')

    # # salva o desenho do circuito
    # salva_circuito(trans_circ, nome_circuito='circuito.png')

    return trans_circ


def gera_circuito_qiskit_comparacao(dados, abordagem):
    abordagens = {
        'unitario': cria_circuito_unitario_qsikit,
        'linear': cria_circuito_linear_qsikit,
        'permutacao': cria_circuito_permutacao,
    }

    if abordagem not in abordagens:
        raise Exception(f'Abordagem {abordagem} desconhecida.')

    # realiza a sintese usando a abordagem informada
    circuito_qiskit = abordagens[abordagem](dados)
    logger.info(f'Circuito {abordagem} gerado (qiskit):\n{circuito_qiskit}')

    # transforma os circuitos qiskit em TFC: obtem QASM
    qasm_circuito = obtem_qasm(circuito_qiskit)
    logger.debug(f'QASM {abordagem}:\n{qasm_circuito}')

    # transforma os circuitos qiskit em TFC: usando o QASM gera o TFC
    circuito_sintese = converte_qasm_em_circuito(qasm_circuito)
    logger.info(f'Circuito {abordagem} TFC:\n{circuito_sintese}')

    return circuito_sintese


def gera_circuitos_para_comparacao(dados, n, salvar_circuitos=False, diretorio_base='./relatorios_sintese/tfcs/', seed=0, t=0):
    dados = converte_permutacao_em_tabela_verdade(dados)

    # obtem a matriz de permutacao associada com os dados
    matriz = gera_matriz_de_permutacao(dados, n)
    logger.info(f'Matriz de permutação associada:\n{matriz}')

    # inicializa um dicionario para armazenar os circuitos
    circuitos_sintese = dict()

    # realiza a sintese com qiskit (alternativa: https://github.com/qiskit-community/qiskit-sat-synthesis)
    circuitos_sintese['unitario'] = gera_circuito_qiskit_comparacao(dados=matriz, abordagem='unitario')

    circuitos_sintese['linear'] = gera_circuito_qiskit_comparacao(dados=matriz, abordagem='linear')

    circuitos_sintese['permutacao'] = gera_circuito_qiskit_comparacao(dados=dados, abordagem='permutacao')

    # realiza a sintese com a nossa abordagem
    circuitos_sintese['reed'] = executa_sintese(n=n, tabela_saida=dados)
    circuitos_sintese['reed'] = processa_tfc(str(circuitos_sintese['reed']))
    logger.info(f'Circuito RM gerado (sintese):\n{circuitos_sintese["reed"]}')

    # salvar em disco?
    if salvar_circuitos:
        for abordagem, circ in circuitos_sintese.items():
            # perm = converte_tabela_verdade_em_permutacao(dados)
            # perm = '.'.join(perm)
            circ.salva_em_arquivo(f'{diretorio_base}/n{n}_s{seed}_t{t:03d}_{abordagem}.tfc')
            # circ.salva_em_arquivo(f'{diretorio_base}/circuito_{abordagem}.tfc')

    return circuitos_sintese


def aplica_comparacao_com_pos_sintese(circuitos_sintese, salvar_circuitos=False,
                                      diretorio_base='./relatorios_sintese/tfcs/'):
    circuitos_pos = dict()

    for abordagem, circuito in circuitos_sintese.items():
        logger.info(f'Executando pos-sintese na abordagem {abordagem}')
        logger.info(f'Circuito Original:\n{circuito}')

        # algumas das operações abaixo são feitas diretamente no circuito, então é necessário criar uma cópia
        circ = circuito.obtem_copia()

        # executa otimizações
        circ = executa_reed(circ)
        circ = executa_regras(circ)
        circ = executa_otimos(circ)

        # armazena o circuito otimizado
        circuitos_pos[abordagem] = circ

        # salvar em disco?
        if salvar_circuitos:
            # perm = circ.obtem_permutacao()
            # perm = '.'.join(perm)
            circ.salva_em_arquivo(f'{diretorio_base}/circuito_{abordagem}_opt.tfc')

    return circuitos_pos


def executa_comparacao_qiskit(seed=10, n_inicial=2, n_final=4, qtd_testes_por_n=10, diretorio='./relatorios_sintese/'):
    """
    Executa a nossa sintese e a sintese do QisKit, e depois otimiza usando a nossa pos sintese.

    @param seed: define a seed para reprodutibilidade.
    @param n_inicial: valor de N inicial.
    @param n_final: valor de N final.
    @param qtd_testes_por_n: quantidade de testes para cada valor de N.
    @param diretorio: onde serão salvos os resultados (em CSV) e os TFCs gerados.
    @return:
    """

    for n in range(n_inicial, n_final + 1):
        # renova a seed
        random.seed(seed)

        for t in range(1, qtd_testes_por_n + 1):
            logger.info(f'Executando teste #{t}')

            dados = gera_permutacao_aleatoria(n)
            logger.info(f'N = {n}')
            logger.info(f'Dados de entrada:\n{dados}')

            # gera os circuitos para comparacao usando QiKit e nosso metodo
            circuitos_sintese = gera_circuitos_para_comparacao(
                dados=dados,
                seed=seed,
                n=n,
                t=t,
                salvar_circuitos=True,
                diretorio_base=f'{diretorio}/tfcs/',
                # diretorio_base=f'{diretorio}/tfcs/n_{n}/seed_{seed}_teste_{t}/',
            )

            # # otimiza usando a pos sintese
            # circuitos_pos = aplica_comparacao_com_pos_sintese(
            #     circuitos_sintese,
            #     salvar_circuitos=True,
            #     diretorio_base=f'{diretorio}/tfcs/n_{n}/seed_{seed}_teste_{t}/'
            # )
            #
            # # salva as informacoes em CSV
            # informacoes = extrai_informacoes_sintese(dados, circuitos_sintese, circuitos_pos)
            # escreve_csv_sintese(nome_arquivo=f'{diretorio}/sintese_n{n}.csv', informacoes=informacoes)


if __name__ == '__main__':
    executa_comparacao_qiskit()
