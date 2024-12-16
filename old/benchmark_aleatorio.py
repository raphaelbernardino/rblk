import csv
import os
import random
from multiprocessing import cpu_count
from pathlib import Path
from typing import List, Iterable

from pebble import ProcessPool

from benchmark_aleatorio_util import le_arquivo_e_reduz_circuitos
from novo.benchmark.benchmark import Benchmark
from novo.circuitos.alvo import Alvo
from novo.circuitos.circuito import Circuito
from novo.circuitos.controle import Controle
from novo.circuitos.states import States
from novo.circuitos.toffoli import Toffoli
from novo.logs.logging_utils import create_logger
from novo.otimizador.analisador_de_janelas import avalia_janelas
from novo.otimizador.otimizador_reed import otimiza_circuito_com_reed

logger = create_logger('benchmark_aleatorio', level='WARN')


def executa_aleatorio(nome_tfc: str, reorganiza: bool = True,
                      aplica_regras: bool = True, aplica_otimos: bool = True,
                      aplica_reed: bool = False):
    """


    @param nome_tfc:
    @param reorganiza:
    @param aplica_regras:
    @param aplica_otimos:
    @param aplica_reed:
    @return:
    """
    circ = le_arquivo_e_reduz_circuitos(nome_tfc, reorganiza=reorganiza,
                                        aplica_regras=aplica_regras, aplica_otimos=aplica_otimos,
                                        aplica_reed=aplica_reed)
    return circ


def executa_aleatorio_com_otimos_e_regras(nome_tfc):
    return executa_aleatorio(nome_tfc, reorganiza=True,
                             aplica_regras=True, aplica_otimos=True,
                             aplica_reed=False)


def executa_aleatorio_com_reed_otimos_e_regras(nome_tfc):
    return executa_aleatorio(nome_tfc, reorganiza=True,
                             aplica_regras=True, aplica_otimos=True,
                             aplica_reed=True)


def gera_controles_aleatorios(qtd_controles_por_porta: int) -> List[Controle]:
    """
    Gera controles aleatórios para serem incluídos numa porta.

    @param qtd_controles_por_porta: a quantidade de controles que uma porta possui
    @return: a lista de controles
    """
    controles = list()

    for i in range(qtd_controles_por_porta):
        x = random.randint(0, 1)
        y = random.randint(0, 1)

        # se x = 1, devo incluir o controle
        if x == 1:
            # se y = 0, controle negativo; c.c. controle positivo
            sinal = States.ctrl_negativo if y == 0 else States.ctrl_positivo

            # cria um controle
            um_controle = Controle(linha=i, sinal=sinal)

            # adiciona o controle na lista de controles
            controles.append(um_controle)
            logger.debug(f'Adicionado um controle {sinal} na linha {i}')

        else:
            logger.debug(f'Adicionado um controle Ausente na linha {i}')

    return controles


def gera_uma_porta(qtd_controles_por_porta: int) -> Toffoli:
    # o alvo ocupa a linha seguinte às ocupadas pelos controles
    alvo = Alvo(linha=qtd_controles_por_porta)
    logger.debug(f'Gerado um alvo: {alvo}')

    # gera os controles aleatórios
    controles = gera_controles_aleatorios(qtd_controles_por_porta)
    logger.debug(f'Controles gerados: {controles}')

    # junta os controles com o alvo
    porta = Toffoli(alvos=alvo, controles=controles)
    logger.debug(f'A porta gerada foi: {porta}')

    return porta


def gera_um_circuito(qtd_portas_por_circuito: int, qtd_controles_por_porta: int) -> Circuito:
    """


    @param qtd_portas_por_circuito:
    @param qtd_controles_por_porta:
    @return:
    """
    # inicia uma nova lista de portas
    portas = list()

    for i in range(qtd_portas_por_circuito):
        # gera uma porta aleatória
        logger.debug(f'Gerando a {i + 1}o porta do circuito')
        porta = gera_uma_porta(qtd_controles_por_porta)

        # adiciona a porta na lista de portas
        portas.append(porta)

    # cria um circuito contendo as portas e usando n = qtd_controles + 1
    circuito = Circuito(portas=portas, qtd_vars=qtd_controles_por_porta + 1)

    return circuito


def gera_circuitos_aleatorios(qtd_circuitos: int, qtd_portas_por_circuito: int,
                              qtd_controles_por_porta: int) -> Iterable[Circuito]:
    """


    @param qtd_circuitos:
    @param qtd_portas_por_circuito:
    @param qtd_controles_por_porta:
    @return:
    """
    for i in range(qtd_circuitos):
        logger.info(f'Gerando o {i + 1}o circuito')
        circuito = gera_um_circuito(qtd_portas_por_circuito, qtd_controles_por_porta)
        logger.info(f'O circuito aleatório resultante é:\n{circuito}')

        # retorna o circuito gerado
        yield circuito


def executa_benchmark_aleatorio(funcao_otimizacao_benchmark,
                                qtd_circuitos: int, qtd_portas: int, qtd_controles: int,
                                nome_relatorio_benchmark: str = 'relatorio.csv',
                                diretorio: str = './benchmark_aleatorio/', seed: int = 199):
    """


    @param qtd_circuitos:
    @param qtd_portas:
    @param qtd_controles:
    @param funcao_otimizacao_benchmark:
    @param nome_relatorio_benchmark:
    @param diretorio:
    @param seed:
    @return:
    """
    diretorio = Path(diretorio)

    # define seed para gerar os mesmos circuitos
    random.seed(seed)

    for i, circ in enumerate(gera_circuitos_aleatorios(qtd_circuitos, qtd_portas, qtd_controles)):
        # gera um nome aleatorio pro circuito
        nome = f'circuito_aleatorio_{i:04d}.tfc'

        # gera o caminho do arquivo
        destino = Path(diretorio, nome)

        # escreve o circuito em disco para que o benchmark seja feito
        circ.salva_em_arquivo(destino)

    # # gera o relatorio de portas dos circuitos originais
    # avalia_janelas(diretorio=str(diretorio),
    #                nome_relatorio=Path(f'./{diretorio}/relatorio_benchmark_aleatorio_original.csv'))

    if funcao_otimizacao_benchmark is not None:
        # executa a otimizacao em cima dos circuitos originais
        bench = Benchmark(diretorio=Path(diretorio), funcao_benchmark=funcao_otimizacao_benchmark,
                          salvar_circuitos=True)

        # gera o relatorio de portas dos circuitos otimizados
        diretorio_bench = bench.obtem_diretorio_benchmark()
        avalia_janelas(diretorio=diretorio_bench, nome_relatorio=nome_relatorio_benchmark)


def executa_benchmarks_aleatorios(funcao_de_otimizacao,
                                  qtd_portas_max=5000, qtd_linhas_max=14, qtd_circuitos_gerados=10,
                                  diretorio_base='', seed=199):
    qtd_portas_de_teste = list(range(500, qtd_portas_max + 1, 500))
    qtd_portas_de_teste[0] = 500

    pool = ProcessPool(max_workers=cpu_count() // 2)
    jobs = list()
    timeout_por_circuito = 5 * 60 * 60  # timeout em segundos: 5 horas

    for qtd_linhas in range(3, qtd_linhas_max + 1, 1):
        qtd_controles_por_porta = qtd_linhas - 1

        for qtd_portas in qtd_portas_de_teste:
            diretorio = Path(diretorio_base, f'n{qtd_linhas}_p{qtd_portas}')
            nome_relatorio = f'relatorio_benchmark_aleatorio_n{qtd_linhas}_p{qtd_portas}.csv'

            destino_relatorio = Path(diretorio, nome_relatorio)

            args = (funcao_de_otimizacao,
                    qtd_circuitos_gerados, qtd_portas, qtd_controles_por_porta,
                    destino_relatorio, diretorio,
                    seed)

            job = pool.schedule(function=executa_benchmark_aleatorio, args=args, timeout=timeout_por_circuito)
            jobs.append(job)

    # espera as threads terminarem
    pool.close()
    pool.join()


def busca_relatorios_benchmark(diretorio):
    if Path(diretorio).is_file():
        yield diretorio

    if not Path(diretorio).exists():
        raise Exception('Directory does not exist!')

    for raiz, subdir, arq in os.walk(diretorio):
        for nome_arq in sorted(arq):
            if nome_arq.startswith('benchmark') and nome_arq.endswith('.csv'):
                nome_arq_completo = os.path.join(raiz, nome_arq)
                # print(f'{nome_arq_completo}')
                yield nome_arq_completo


def realiza_leitura_benchmark(local_arquivo) -> dict:
    with open(local_arquivo, 'r') as f:
        r = csv.DictReader(f)

        for linha in r:
            yield linha


def escreve_relatorio_consolidado(local_arquivo, informacoes):
    cabecalho = ['N', 'P', 'Nome TFC',
                 'GC Original', 'QC Original',
                 'GC Otimizado', 'QC Otimizado',
                 'Diff GC', 'Diff QC']

    local_arquivo = Path(local_arquivo)
    if not local_arquivo.parent.exists():
        local_arquivo.parent.mkdir(parents=True, exist_ok=True)

    with open(local_arquivo, 'w') as f:
        w = csv.writer(f)

        # escreve o cabecalho
        w.writerow(cabecalho)

        # escreve o conteudo
        w.writerows(informacoes)


def consolida_relatorios(diretorio_relatorios: str, nome_relatorio='consolidado.csv'):
    informacoes = list()
    relatorios = busca_relatorios_benchmark(diretorio_relatorios)

    for relatorio in relatorios:
        logger.debug(f'Nome Relatorio: {relatorio}')

        # obtem o valor de bits usados (N) e a quantidade de portas (P)
        diretorio_pai = Path(relatorio).parent.name
        n, p = diretorio_pai.split('_')
        n, p = int(n[1:]), int(p[1:])

        for info in realiza_leitura_benchmark(relatorio):
            # obtem as informacoes do relatorio
            info_as_val = list(info.values())

            # monta a informacao completa, adicionando os valores N e P
            informacao = [n, p]
            informacao.extend(info_as_val)

            # agrupa a informacao para posterior escrita
            informacoes.append(informacao)

    local_relatorio_consolidado = Path(diretorio_relatorios) / Path(nome_relatorio)
    escreve_relatorio_consolidado(local_relatorio_consolidado, sorted(informacoes))


def main():
    executa_benchmarks_aleatorios(funcao_de_otimizacao=executa_aleatorio_com_otimos_e_regras,
                                  diretorio_base='./benchmark_aleatorio/benchmark_aleatorio_otimos_regras/')
    consolida_relatorios('./benchmark_aleatorio_otimos_regras/')

    executa_benchmarks_aleatorios(funcao_de_otimizacao=executa_aleatorio_com_reed_otimos_e_regras,
                                  diretorio_base='./benchmark_aleatorio/benchmark_aleatorio_reed_otimos_regras/')
    consolida_relatorios('./benchmark_aleatorio_reed_otimos_regras/')

    executa_benchmarks_aleatorios(funcao_de_otimizacao=otimiza_circuito_com_reed,
                                  diretorio_base='./benchmark_aleatorio/benchmark_aleatorio_reed/')
    consolida_relatorios('./benchmark_aleatorio_reed/')

    """
    nome_relatorio = './benchmark_aleatorio/relatorio_benchmark_aleatorio_otimizado_otimos_regras.csv'
    
    ------------------
    
    diretorio = './benchmark_aleatorio_kowada/'
    funcao_otimizacao = executa_aleatorio_com_reed_otimos_e_regras
    nome_relatorio = './benchmark_aleatorio/relatorio_benchmark_aleatorio_otimizado_kowada.csv'
    # """


if __name__ == '__main__':
    main()
