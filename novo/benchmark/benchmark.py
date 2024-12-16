import csv
from datetime import datetime
from multiprocessing import cpu_count
from pathlib import Path

from pebble import ProcessPool

from novo.benchmark.benchmark_util import busca_arquivos_tfc
from novo.logs.logging_utils import create_logger
from novo.otimizador.otimizador_util import realiza_leitura_tfc, verifica_otimizacao

logger = create_logger(name='benchmark', level='DEBUG', use_filehandler=True)


class Benchmark:

    def __init__(self, diretorio, funcao_benchmark, nome_arquivo=None, salvar_circuitos=False, qtd_threads=None):
        """

        :param diretorio: Lista de diretórios a serem utilizados no benchmark.
        :param funcao_benchmark: A função que será executada para cada circuito.
        :param nome_arquivo: Nome do arquivos onde será salvo as informações do benchmark realizado (arquivo CSV).
        :param salvar_circuitos: Indica se os circuitos otimizados devem ser salvos ou não.
        :param qtd_threads: A quantidade de threads a serem utilizadas para execução paralela do benchmark.
        """
        self.__arquivos = self.__busca_arquivos(diretorio)
        self.__funcao = funcao_benchmark

        # obtem a data de execução do benchmark
        self.__data_execucao = datetime.now().strftime('%Y-%m-%d')

        # constrói o nome do arquivo benchmark
        # self.__nome_arquivo = Path(f'./{diretorio}/benchmark_{self.__data_execucao}.csv')
        self.__nome_arquivo = Path(f'./{diretorio}/benchmark.csv')
        if nome_arquivo is not None:
            self.__nome_arquivo = Path(nome_arquivo)

        # corrige a extensão do nome do arquivo benchmark para CSV
        if self.__nome_arquivo.suffix != '.csv':
            self.__nome_arquivo = Path(self.__nome_arquivo.parent, self.__nome_arquivo.name + '.csv')

        # constrói o nome do diretorio benchmark
        # self.__diretorio_benchmark = Path(self.__nome_arquivo.parent, f'{self.__data_execucao}')
        self.__diretorio_benchmark = Path(self.__nome_arquivo.parent, 'tfcs_otimizados')

        # define se os circuitos otimizados devem ser salvos
        self.__deve_salvar = salvar_circuitos

        # define a quantidade de threads a serem utilizadas
        self.__qtd_threads = qtd_threads
        if self.__qtd_threads is None:
            self.__qtd_threads = cpu_count() // 2

        # # cria um controle para escrita do arquivo
        # self.__lock = threading.Lock()

        # inicia o benchmark
        self.executa()

    def obtem_nome_arquivo(self):
        return self.__nome_arquivo

    def obtem_diretorio_benchmark(self):
        return self.__diretorio_benchmark

    @staticmethod
    def __busca_arquivos(caminho):
        diretorios = caminho
        arquivos = set()

        if not (type(caminho) in [list, tuple, set]):
            diretorios = [caminho]

        for diretorio in diretorios:
            arquivos_diretorio = busca_arquivos_tfc(diretorio)

            for arquivo in arquivos_diretorio:
                arquivos.add(arquivo)

        return sorted(arquivos)

    def executa(self):
        total_arquivos = len(self.__arquivos)

        # gera e escreve o cabeçalho
        cabecalho = self.gera_cabecalho()
        self.escreve_csv(cabecalho)

        # cria as threads para executar em paralelo
        pool = ProcessPool(max_workers=self.__qtd_threads)
        jobs = list()
        logger.info(f'Executando o benchmark com {self.__qtd_threads} threads...')

        for i, arquivo in enumerate(self.__arquivos):
            logger.info(f'Submetendo: {arquivo} ({i+1} de {total_arquivos} :: {100 * i / total_arquivos:.0f}%)')
            # self.processa_arquivo(arquivo)
            args = (arquivo,)
            job = pool.schedule(function=self.processa_arquivo, args=args)
            jobs.append(job)

        # fecha a pool (não aceita mais nenhum job)
        pool.close()

        # espera as threads terminarem
        pool.join()

    def processa_arquivo(self, arquivo):
        info_adicional = ''

        circ_original = realiza_leitura_tfc(arquivo)
        logger.info(f'Processando: {arquivo}')
        logger.debug(f'Circuito GC = {circ_original.gc} \t QC = {circ_original.qc}')

        # nome_novo = f'benchmark_{self.__data_execucao}_{Path(arquivo).name}'
        nome_novo = f'{Path(arquivo).name}'
        destino_novo = Path(self.obtem_diretorio_benchmark(), nome_novo)

        if destino_novo.exists():
            logger.info(f'Circuito já foi processado anteriormente. Passando para o próximo...')
            return

        # em caso de erro, otimizado é null
        circ_otimizado = None

        try:
            circ_otimizado = self.__funcao(arquivo)

            # verifica se a otimização foi feita de forma correta
            logger.info(f'Verificando permutação do circuito {arquivo}')
            verifica_otimizacao(circ_original, circ_otimizado)

        except Exception as e:
            logger.error(f'Erro ao processar: {arquivo}\nErro: {e}')
            info_adicional = f'Erro: {e}'

        finally:
            logger.info(f'Salvando o circuito otimizado {arquivo} --> {destino_novo}')
            if self.__deve_salvar and circ_otimizado is not None:
                circ_otimizado.salva_em_arquivo(destino_novo)

            informacao = self.extrai_informacao_circuito(arquivo, circ_original, circ_otimizado,
                                                         obs=info_adicional)
            self.escreve_csv(informacao)

    def extrai_informacao_circuito(self, arquivo, circuito_original, circuito_otimizado, valor_nulo='-', obs=''):
        # extrai informacoes do circuito original
        nome_tfc = Path(arquivo).name
        gc_original, qc_original, l_original = self.extrai_custos_do_circuito(circuito_original)

        # valor padrão para quando o circuito não pode ser otimizado
        gc_otimizado, qc_otimizado, l_otimizado = valor_nulo, valor_nulo, valor_nulo
        diff_gc, diff_qc, diff_l = valor_nulo, valor_nulo, valor_nulo

        if circuito_otimizado is not None:
            # extrai informacoes do circuito original
            gc_otimizado, qc_otimizado, l_otimizado = self.extrai_custos_do_circuito(circuito_otimizado)

            # calcula otimizacao feita
            diff_gc = gc_original - gc_otimizado
            diff_qc = qc_original - qc_otimizado
            diff_l = l_original - l_otimizado

        # info_temp = extrai_informacoes(circuito_otimizado, nome_tfc)
        # qtd_subcircuitos = info_temp[2]
        # tam_medio_janelas = info_temp[3]
        # maior_janela = info_temp[4]
        # menor_janela = info_temp[5]
        # observacao = info_temp[6]
        # obs += f'\n{observacao}'.strip()

        # organiza informacoes sobre o circuito
        informacao = list()
        informacao += [nome_tfc, gc_original, qc_original]
        informacao += [l_original]
        # informacao += [qtd_subcircuitos]
        # informacao += [tam_medio_janelas, maior_janela, menor_janela]
        informacao += [gc_otimizado, qc_otimizado]
        informacao += [l_otimizado]
        informacao += [diff_gc, diff_qc, diff_l]
        informacao += [obs]

        return informacao

    def __escreve_csv(self, modo, informacoes):
        with open(self.__nome_arquivo, modo) as f:
            w = csv.writer(f)
            w.writerow(informacoes)

    def escreve_csv(self, informacoes, modo='a'):
        try:
            if not self.__nome_arquivo.parent.exists():
                self.__nome_arquivo.parent.mkdir(parents=True, exist_ok=True)

            # with self.__lock:
            self.__escreve_csv(modo, informacoes)

        except Exception as e:
            raise e

    @staticmethod
    def extrai_custos_do_circuito(circuito):
        return circuito.gc, circuito.qc, len(circuito.obtem_linhas_usadas())

    @staticmethod
    def gera_cabecalho():
        cabecalho = list()

        cabecalho.append('Nome TFC')
        cabecalho.append('GC Original')
        cabecalho.append('QC Original')
        cabecalho.append('L Original')
        # cabecalho.append('Qtd. Subcircuitos')
        # cabecalho.append('Tam. Medio Janelas')
        # cabecalho.append('Maior Janela')
        # cabecalho.append('Menor Janela')
        cabecalho.append('GC Otimizado')
        cabecalho.append('QC Otimizado')
        cabecalho.append('L Otimizado')
        cabecalho.append('Diff GC')
        cabecalho.append('Diff QC')
        cabecalho.append('Diff L')
        cabecalho.append('Observações')

        return cabecalho
