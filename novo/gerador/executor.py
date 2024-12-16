from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import product, islice, permutations
from math import factorial
from multiprocessing import Manager
from os import cpu_count

from novo.circuitos.circuito import Circuito
from novo.gerador.gerador_de_circuitos import define_portas_toffoli, escolhe_melhor_circuito
from novo.gerador.gerador_util import salva_circuitos_minimos
from novo.logs.logging_utils import create_logger

logger = create_logger('gerador_executor', level='DEBUG')


def processa_permutacao(circuitos, qtd_bits, dic):
    for circuito in circuitos:
        circ = Circuito(circuito, qtd_bits)
        # logger.info(f'Circ?\n{circ}')
        # sleep(2)

        # # obtem alvos e verifica se deve processar
        # alvos = circ.obtem_linhas_de_alvo_usadas()
        # # logger.info(f'Alvos? {alvos}')
        # if alvos != {0}:
        #     continue

        permutacao = circ.obtem_permutacao(qtd_bits=qtd_bits)

        # logger.debug(f'Circuito = {circ} :: Permutacao = {permutacao} :: {len(dic)}')
        # sleep(1)

        melhor = dic.get(permutacao)
        if melhor is None:
            dic[permutacao] = circ
        else:
            dic[permutacao] = escolhe_melhor_circuito(melhor, circ)


# https://docs.python.org/3/library/itertools.html#itertools.batched
def batched(iterable, n):
    if n < 1:
        raise ValueError('n must be at least one')

    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def gera_combinacoes(portas, qtd, tamanho_fatia=2_000):
    combinacoes = product(portas, repeat=qtd)

    for fatia in batched(combinacoes, tamanho_fatia):
        yield fatia


def gera_estados_iniciais(qtd_bits, resultados):
    bits = [''.join(p) for p in product('01', repeat=qtd_bits)]

    for estado in permutations(bits):
        resultados[estado] = None

    resultados[tuple(bits)] = Circuito()


def main(qtd_max_bits=3, nome_circuitos='circuitos'):
    n_workers = cpu_count() // 2
    thread_pool = ThreadPoolExecutor(max_workers=n_workers)
    logger.debug(f'Usando {n_workers} workers...')

    for qtd_bits in range(1, qtd_max_bits + 1):
        logger.debug(f'Testando {qtd_bits} bits...')
        casos_totais = factorial(2 ** qtd_bits)
        resultados = Manager().dict()

        # preenche o dicionário de resultados com os estados iniciais
        # gera_estados_iniciais(qtd_bits, resultados)

        # define as portas que serão usadas
        portas = define_portas_toffoli(qtd_bits)
        # for i, porta in enumerate(portas):
        #     logger.info(f'n={qtd_bits} :: Porta #{i}: {porta}')
        # sleep(1)

        qtd_portas = 0
        while len(resultados) < casos_totais:
            jobs = list()

            for combinacao in gera_combinacoes(portas, qtd_portas):
                # logger.info(f'Combinacao:: {combinacao}')
                logger.info(f'Submetendo job #{len(jobs) + 1}...')
                job = thread_pool.submit(processa_permutacao, combinacao, qtd_bits, resultados)
                jobs.append(job)
                # sleep(2)

            tarefas_faltantes = len(jobs)
            for _ in as_completed(jobs):
                tarefas_faltantes -= 1
                logger.debug(f'Tarefas restantes (n={qtd_bits}, qtd_portas={qtd_portas}): {tarefas_faltantes}')

            qtd_portas += 1

            # salva os resultados encontrados
            logger.info(f'Resultados (n={qtd_bits}) ==> {len(resultados)}')
            # for k, v in resultados.items():
            #     logger.debug(f'P: {k}, C: {v}')
            salva_circuitos_minimos(circuitos=resultados, qtd_bits=qtd_bits, nome=nome_circuitos)

    # termina as threads faltantes, esperando as que estão em execução
    thread_pool.shutdown(wait=True, cancel_futures=False)


if __name__ == '__main__':
    main(qtd_max_bits=3, nome_circuitos='toffoliParalela')
