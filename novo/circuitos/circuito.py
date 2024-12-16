import copy
import time
from pathlib import Path

import numpy as np

from novo.circuitos.circuitos_util import gera_tabela_verdade, gera_permutacao, inverte_elementos
from novo.logs.logging_utils import create_logger

logger = create_logger(name='circuito', level='DEBUG')


class Circuito:
    def __init__(self, portas=None, qtd_vars=0, ancillas=0, mapa=None):
        """
            Recebe uma lista de portas e quantidade de variaveis.
        :param portas: Uma lista de Portas do tipo Fredkin ou Toffoli.
        :param qtd_vars: Uma quantidade inteira que representa a quantidade de variaveis.
        """
        self.bits_extras = ancillas
        self.tamanho_circuito = qtd_vars

        self.portas = portas
        if self.portas is None:
            self.portas = list()

        self.mapeamento = mapa
        if self.mapeamento is None:
            mapa = [(i, i) for i in range(self.tamanho_circuito)]
            self.mapeamento = dict(mapa)

        if self.tamanho_circuito is None:
            self.tamanho_circuito = self.__obtem_quantidade_de_variaveis()

        self.portas = self.__adiciona_portas(portas)

        ### apesar de achar que deve ser um atributo, demanda muito tempo gerar a tabela vdd a cada inicializacao
        # self.tabela_verdade = self.obtem_tabela_verdade()
        self.gc = self.custo_porta()
        self.qc = self.custo_quantico()

    def __adiciona_portas(self, info):
        if info is None:
            info = list()

        if isinstance(info, Circuito):
            info = info.portas

        if isinstance(info, tuple):
            info = list(info)

        if isinstance(info, list):
            portas = list()

            for p in info:
                ptemp = copy.deepcopy(p)
                ptemp.mapeamento = self.mapeamento
                portas.append(ptemp)

            return portas

        raise Exception('Circuito:: Operação não suportada!')

    def __obtem_quantidade_de_variaveis(self):
        linhas_usadas = self.obtem_linhas_usadas()
        return len(linhas_usadas)

    def obtem_mapeamentos(self):
        mapa = f'Mapeamento do Circuito: {self.mapeamento}'

        mapa += f'\nMapeamento das portas:'
        for porta in self.portas:
            mapa += f'\n\t{porta} ==> {porta.mapeamento}'

        return mapa

    def obtem_quantidade_de_bits(self):
        return self.tamanho_circuito + self.bits_extras

    def atualiza_informacoes(self):
        """
        Atualiza informações sobre o circuito.

        @return:
        """
        # self.tamanho_circuito = self.__obtem_quantidade_de_variaveis()
        self.tamanho_circuito = 1 + max(self.obtem_linhas_usadas(), default=0)
        self.gc = self.custo_porta()
        self.qc = self.custo_quantico()

    def obtem_copia(self):
        return copy.deepcopy(self)

    def reduz_linhas(self):
        mapeamento = dict()
        ini_vars = self.tamanho_circuito
        ini_ancs = self.bits_extras

        linhas = self.obtem_linhas_usadas()
        linhas = list(linhas)
        # logger.debug(f'Linhas: {linhas}')

        for i in range(0, ini_vars):
            if i not in linhas:
                self.tamanho_circuito -= 1
                continue

            mapeamento[i] = linhas.index(i)

        for i in range(ini_vars, ini_vars + ini_ancs):
            if i not in linhas:
                self.bits_extras -= 1
                continue

            mapeamento[i] = linhas.index(i)

        # logger.debug(f'MAP: {mapeamento}')

        for porta in self.portas:
            porta.modifica_linhas(mapeamento)

    def obtem_linhas_de_alvo_usadas(self):
        linhas_usadas = set()

        for porta in self.portas:
            linhas = porta.obtem_linhas_de_alvo_usadas()
            linhas_usadas = linhas_usadas.union(linhas)

        return linhas_usadas

    def obtem_linhas_de_controle_usadas(self):
        linhas_usadas = set()

        for porta in self.portas:
            linhas = porta.obtem_linhas_de_controle_usadas()
            linhas_usadas = linhas_usadas.union(linhas)

        return linhas_usadas

    def obtem_linhas_usadas(self):
        linhas_de_alvo = self.obtem_linhas_de_alvo_usadas()
        linhas_de_controle = self.obtem_linhas_de_controle_usadas()

        linhas_usadas = linhas_de_alvo.union(linhas_de_controle)
        return linhas_usadas

    def apaga_porta_por_indice(self, indice):
        del self.portas[indice]
        self.atualiza_informacoes()

    # def remove_porta(self, porta):
    #     self.portas.remove(porta)
    #     self.__atualiza_informacoes()

    def insere_porta_por_indice(self, indice, porta):
        self.portas.insert(indice, porta)
        self.atualiza_informacoes()

    # def adiciona_porta(self, porta):
    #    uma_porta = copy.deepcopy(porta)
    #    self.portas.append(uma_porta)
    #    self.__atualiza_informacoes()

    def custo_porta(self):
        return len(self.portas)

    def custo_quantico(self):
        custo_total = 0

        for porta in self.portas:
            custo_total += porta.calcula_custo_quantico()

        return custo_total

    def custo_cnot(self):
        custo_total = 0

        for porta in self.portas:
            # logger.debug(f'Porta: {porta}')
            custo = porta.calcula_custo_cnot()
            # logger.debug(f'Custo: {custo}')
            custo_total += custo
            # logger.debug(f'Total: {custo_total}')

        return custo_total

    def calcula_tamanho(self):
        linhas_usadas = self.obtem_linhas_usadas()
        return max(linhas_usadas)

    def obtem_permutacao(self, qtd_bits=None):
        if qtd_bits is None:
            qtd_bits = self.obtem_quantidade_de_bits()

        elementos = gera_permutacao(qtd_bits)
        # logger.debug(f'Permutacao Inicial: {elementos}')
        # logger.debug(f'Mapeamento: {self.mapeamento}')

        inverte_elementos(elementos)
        for porta in self.portas:
            # logger.debug(f'Aplicando {porta}')
            porta.roda_porta_permutacao(elementos)
            # logger.debug(f'Aplicado {elementos}')
        inverte_elementos(elementos)

        return tuple(elementos)

    def obtem_tabela_verdade(self, n=None, ancillas=None):
        if n is None:
            n = self.tamanho_circuito

        if ancillas is None:
            ancillas = self.bits_extras

        tab_vdd = gera_tabela_verdade(n, ancillas=ancillas)
        # tabela_verdade = list(tab_vdd)
        tabela_verdade = np.fromiter(tab_vdd, dtype=np.dtype((np.uint8, n)), count=2**n)
        # tabela_verdade = np.zeros(shape=(2**n, n), dtype=np.uint8)
        # for i, k in enumerate(tab_vdd):
        #     tabela_verdade[i] = k

        for porta in self.portas:
            porta.roda_porta_tabela_verdade(tabela_verdade)

        return tabela_verdade

    def obtem_portas_string(self):
        s = [str(porta) for porta in self.portas]
        return s

    def salva_em_arquivo(self, nome_do_arquivo=None):
        conteudo = str(self)

        if nome_do_arquivo is None:
            timestamp = time.time()
            nome_do_arquivo = Path(f'./data/circuitos/{timestamp}_GC-{self.gc}_QC-{self.qc}.tfc')

        # safety-check
        arquivo = Path(nome_do_arquivo)
        arquivo.parent.mkdir(parents=True, exist_ok=True)

        arquivo.write_text(conteudo)

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            raise Exception('Tipo Circuito somente pode ser concatenado com outro de mesmo tipo.')

        # portas_invertidas = other.portas[::-1]
        # novas_portas = self.portas + portas_invertidas
        novas_portas = self.portas + other.portas
        nova_qtd_vars = max(self.tamanho_circuito, other.tamanho_circuito)
        novos_ancillas = max(self.bits_extras, other.bits_extras)

        novo_circuito = Circuito(novas_portas, nova_qtd_vars, novos_ancillas)

        # linhas_usadas = novo_circuito.__obtem_quantidade_de_variaveis()
        # novo_circuito.bits_extras = linhas_usadas - nova_qtd_vars

        # linhas_usadas = novo_circuito.obtem_linhas_usadas()
        # if len(linhas_usadas) > 0:
        #    novo_circuito.bits_extras = 1 + max(linhas_usadas) - nova_qtd_vars

        return novo_circuito

    def __repr__(self):
        s = ''
        s += f'# GATE_COUNT = {self.gc} \t\t QUANTUM_COST = {self.qc} \t\t ANCILLAS = {self.bits_extras}\n'

        # k = ','.join([f'b{i}' for i in sorted(self.obtem_linhas_usadas())])
        k = ','.join([f'b{i}' for i in range(self.tamanho_circuito + self.bits_extras)])
        s += f'.v {k}\n'
        s += f'.i {k}\n'
        s += f'.o {k}\n'

        s += 'BEGIN\n'
        for porta in self.portas:
            s += str(porta)
            s += '\n'

        s += 'END'
        return s

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.tamanho_circuito != other.tamanho_circuito:
            return False

        if len(self.portas) != len(other.portas):
            return False

        if self.portas != other.portas:
            return False

        return True

    def __lt__(self, other):
        return self.tamanho_circuito < other.tamanho_circuito

    def __len__(self):
        return len(self.portas)

    def __iter__(self):
        for porta in self.portas:
            yield porta
