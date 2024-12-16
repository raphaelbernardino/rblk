import csv
from concurrent.futures import wait, Future
from multiprocessing import Manager, cpu_count
from pathlib import Path
from typing import List

from pebble import ProcessPool

from novo.benchmark.benchmark_util import busca_arquivos_tfc
from novo.circuitos.circuito import Circuito
from novo.logs.logging_utils import create_logger
from novo.otimizador.otimizador_de_circuitos import reorganiza_usando_swaps3
from novo.otimizador.otimizador_util import realiza_leitura_tfc, gera_subcircuitos_usando_alvos3, verifica_otimizacao

logger = create_logger(name='analisador_de_janelas', level='DEBUG')


def salva_informacoes(nome_arquivo: str, info: list):
    try:
        # garante que o diretorio existe (crie caso necessario)
        Path(nome_arquivo).parent.mkdir(parents=True, exist_ok=True)

        with open(nome_arquivo, 'w') as f:
            w = csv.writer(f)
            w.writerows(info)

    except Exception as e:
        raise e


def encontra_menor_e_maior_janela(subcircuitos: List[Circuito]):
    maior_janela = menor_janela = len(subcircuitos[0])

    for i, subcirc in enumerate(subcircuitos):
        logger.debug(f'Subcircuito #{i}: {subcirc}')

        janela = len(subcirc)
        maior_janela = max(janela, maior_janela)
        menor_janela = min(janela, menor_janela)

        logger.debug(f'Maior Janela: {maior_janela}')
        logger.debug(f'Menor Janela: {menor_janela}')

    return maior_janela, menor_janela


def extrai_informacoes(circuito_organizado: Circuito, nome_tfc: str, msg_erro: str = ''):
    info = list()
    info.append(nome_tfc)

    subcircuitos = gera_subcircuitos_usando_alvos3(circuito=circuito_organizado, qtd_alvos=1)

    tamanho_do_circuito = len(circuito_organizado)
    info.append(tamanho_do_circuito)
    logger.info(f'Arquivo TFC: {nome_tfc}')
    logger.info(f'Tamanho total do Circuito (qtd. portas): {tamanho_do_circuito}')

    qtd_de_janelas = len(subcircuitos)
    info.append(qtd_de_janelas)
    logger.info(f'Qtd. de subcircuitos: {qtd_de_janelas}')

    tamanho_medio_das_janelas = tamanho_do_circuito / qtd_de_janelas
    info.append(tamanho_medio_das_janelas)
    logger.info(f'Tamanho Médio das Janelas: {tamanho_medio_das_janelas}')

    maior_janela, menor_janela = encontra_menor_e_maior_janela(subcircuitos)
    info.append(maior_janela)
    info.append(menor_janela)
    logger.info(f'Maior Janela: {maior_janela}')
    logger.info(f'Menor Janela: {menor_janela}')

    info.append(msg_erro)

    return info


def avalia_janela_(circ, nome_tfc):
    circuito_organizado = reorganiza_usando_swaps3(circ)

    msg_erro = verifica_otimizacao(circuito_original=circ,
                                   circuito_otimizado=circuito_organizado,
                                   lanca_erro=False)

    info = extrai_informacoes(circuito_organizado, nome_tfc, msg_erro)

    return info


def avalia_janela(nome_tfc, relatorio):
    logger.info(f'Processando arquivo TFC: {nome_tfc}')
    circuito = realiza_leitura_tfc(nome_tfc)

    relatorio[nome_tfc] = avalia_janela_(circuito, nome_tfc)


def espera_thread(job, timeout):
    """ timeout em segundos """
    wait([job], timeout=timeout)


def espera_threads(jobs: List[Future], timeout: int = 1):
    completos = set()
    jobs_ = set(jobs)

    for job in jobs_:
        espera_thread(job, timeout)

        if not job.done():
            job.cancel()
        else:
            completos.add(job)

    incompletos = jobs_ - completos
    return completos, incompletos


def avalia_janelas(diretorio: str, nome_relatorio: str, timeout_por_circuito: int = 3600):
    """
    Analisa as janelas de cada circuito contido no diretorio informado.
    :param diretorio: O caminho para o diretorio a ser analisado.
    :param nome_relatorio: O caminho onde o relatorio deve ser salvo, incluindo o nome do relatorio.
    :param timeout_por_circuito: Tempo maximo, em segundos, que deve ser gasto analisando cada circuito. Padrão: 1h;
    :return:
    """
    arquivos_tfc = busca_arquivos_tfc(diretorio)

    relatorio = list()
    cabecalho = ['Nome TFC',
                 'Qtd. Portas',
                 'Qtd. Subcircuitos',
                 'Tamanho Médio das Janelas',
                 'Maior Janela',
                 'Menor Janela',
                 'Observacao',
                 ]
    relatorio.append(cabecalho)

    resultados = Manager().dict()
    # pool = ThreadPoolExecutor(max_workers=cpu_count())
    pool = ProcessPool(max_workers=cpu_count() // 2)
    jobs = list()

    for nome_tfc in arquivos_tfc:
        resultados[nome_tfc] = [nome_tfc, '-', '-', '-', '-', '-']

        # job = pool.submit(avalia_janela, nome_tfc, resultados)
        args = (nome_tfc, resultados)
        job = pool.schedule(function=avalia_janela, args=args, timeout=timeout_por_circuito)
        jobs.append(job)

    # fecha a pool (não aceita mais nenhum job)
    pool.close()

    # espera as threads terminarem
    completos, incompletos = espera_threads(jobs, timeout=timeout_por_circuito)
    logger.info(f'Circuitos executados: {len(completos)}, Timeouts: {len(incompletos)}, Total: {len(jobs)}')
    # pool.shutdown(wait=False, cancel_futures=True)
    pool.join()

    # junta as informacoes das threads
    # logger.debug(f'R: {len(resultados)}')
    for _, resultado in resultados.items():
        relatorio.append(resultado)

    # salva o relatorio
    salva_informacoes(nome_relatorio, relatorio)


if __name__ == '__main__':
    # avalia_janelas(diretorio='./temporarios/tfcs_reais/edinelco/',
    #                nome_relatorio='./relatorios/relatorio_edinelco.csv')

    # avalia_janelas(diretorio='./temporarios/tfcs_reais/zakablukov/',
    #                nome_relatorio='./relatorios/relatorio_zakablukov.csv')

    # avalia_janelas(diretorio='./temporarios/tfcs_reais/revlib/n_09-10/',
    #                nome_relatorio='./relatorios/relatorio_revlib_pequenos.csv')

    # avalia_janelas(diretorio='./temporarios/tfcs_reais/revlib/n_10-14/',
    #                nome_relatorio='./relatorios/relatorio_revlib_medianos.csv')

    # avalia_janelas(diretorio='./temporarios/tfcs_reais/revlib/n_15-99/',
    #                nome_relatorio='./relatorios/relatorio_revlib_grandes.csv')

    # avalia_janelas(diretorio='./tfcs/comparacao_artigo_korea/para_testar',
    #                nome_relatorio='./benchmark/relatorio_artigo_korea.csv')

    avalia_janelas(diretorio='./benchmark/2024-07-11_com_reed_muller_e_reorganiza3/',
                   nome_relatorio='./benchmark/relatorio_artigo_korea_otimizacao_reed3.csv')

    avalia_janelas(diretorio='./benchmark/2024-07-08_sem_reed_muller/',
                   nome_relatorio='./benchmark/relatorio_artigo_korea_otimizacao_sem_reed.csv')
