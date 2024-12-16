import copy
from typing import List

from novo.circuitos.alvo import Alvo
from novo.circuitos.controle import Controle


class Toffoli:
    def __init__(self, alvos: List[Alvo], controles: List[Controle], mapa=None):
        self.tamanho_bits = 1 + len(controles)

        self.mapeamento = mapa
        if mapa is None:
            # k = [(i, i) for i in range(self.tamanho_bits)]

            # busca a maior linha de alvo
            maior_linha_alvo = 0
            if isinstance(alvos, list):
                maior_linha_alvo = alvos[0].linha
            elif isinstance(alvos, Alvo):
                maior_linha_alvo = alvos.linha
            else:
                raise Exception(f'Alvo não possui um tipo identificavel. (alvos: {type(alvos)})')

            # busca a maior linha de controle
            maior_linha_controle = 0
            if len(controles) > 0:
                maior_linha_controle = max([ctrl.linha for ctrl in controles])

            # identifica a maior linha entre controles e alvos
            maior_linha = max(maior_linha_alvo, maior_linha_controle)
            # print(f'Maior linha:: {maior_linha_alvo} :: {maior_linha_controle} ==> {maior_linha}')

            # gera o mapeamento a partir da maior linha
            k = [(i, i) for i in range(maior_linha + 1)]
            self.mapeamento = dict(k)

        self.alvos = self.__inicializa_alvos(alvos)
        self.controles = self.__inicializa_controles(controles)

    # def mapeia(self, mapa):
    #     # realiza mapeamento do alvo
    #     self.alvos.mapeia(mapa)
    #
    #     # realiza mapeamento dos controles
    #     for controle in self.controles:
    #         controle.mapeia(mapa)

    def modifica_linhas(self, mapeamento: dict):
        """
        Modifica a linha atual através de mapeamento.

        @param mapeamento: Um dicionário contendo o mapeamento a ser realizado.
        """
        linha_alvo = self.alvos.linha
        nova_linha_alvo = mapeamento[linha_alvo]

        diferenca_linha = linha_alvo - nova_linha_alvo
        self.alvos.modifica_linha(diferenca_linha)

        for ctrl in self.controles:
            linha_ctrl = ctrl.linha
            nova_linha_ctrl = mapeamento[linha_ctrl]

            diferenca_linha = linha_ctrl - nova_linha_ctrl
            ctrl.modifica_linha(diferenca_linha)

    def __inicializa_alvos(self, alvos):
        alvo = list()

        if isinstance(alvos, Alvo):
            um_alvo = copy.deepcopy(alvos)
            um_alvo.linha_original = alvos.linha
            um_alvo.linha = self.mapeamento[alvos.linha]
            alvo.append(um_alvo)

        if isinstance(alvos, list):
            # alvo = [copy.deepcopy(a) for a in alvos]
            for a in alvos:
                um_alvo = copy.deepcopy(a)
                um_alvo.linha_original = a.linha
                # print(f'Mapeamento: {self.mapeamento}')
                # print(f'Alvos: {alvos}')
                # print(f'Linha: {a.linha}')
                # print(f'um_alvo: {um_alvo} :: {um_alvo.linha} :: {um_alvo.linha_original}')
                um_alvo.linha = self.mapeamento[a.linha]
                alvo.append(um_alvo)

        if isinstance(alvos, int):
            um_alvo = Alvo(alvos, self.mapeamento)
            alvo.append(um_alvo)

        if len(alvo) != 1:
            raise Exception('Alvos inválidos! É necessário apenas um alvo.')

        return alvo[0]

    def __inicializa_controles(self, ctrls: List[Controle]):
        controles = list()

        for ctrl in ctrls:
            um_controle = copy.deepcopy(ctrl)
            # print(f'Mapeamento: {self.mapeamento}')
            # print(f'Linha Original: {ctrl.linha} :: {um_controle.linha_original} :: {um_controle.linha}')
            um_controle.linha_original = ctrl.linha
            um_controle.linha = self.mapeamento[ctrl.linha]
            controles.append(um_controle)

        return controles

    def remapeia(self, mapa):
        self.alvos.remapeia(mapa)

        for ctrl in self.controles:
            ctrl.remapeia(mapa)

    def adiciona_controles(self, controles):
        # linhas_usadas = self.obtem_linhas_de_controle_usadas()
        linhas_usadas = self.obtem_linhas_usadas()
        controles_antigos = copy.deepcopy(self.controles)

        for ctrl in controles:
            if ctrl.linha in linhas_usadas:
                self.controles = controles_antigos
                raise Exception('Linha {ctrl.linha} já está ocupada')

            um_controle = copy.deepcopy(ctrl)
            self.controles.append(um_controle)
            self.tamanho_bits = len(self.obtem_linhas_usadas())

    def remove_controle(self, ctrl):
        if ctrl in self.controles:
            self.controles.remove(ctrl)
            self.tamanho_bits = len(self.obtem_linhas_usadas())

    def remove_controles(self, controles):
        for ctrl in controles:
            self.remove_controle(ctrl)

    def obtem_alvos(self):
        return [self.alvos]

    def obtem_copia(self):
        return copy.deepcopy(self)

    def calcula_custo_cnot(self):
        """
        Calcula o custo de CNOTs a partir da quantidade de controles usados.
        Usando como referência o artigo: https://iopscience.iop.org/article/10.1088/2058-9565/acaf9d/meta
        Automatic generation of Grover quantum oracles for arbitrary data structures. Raphael Seidel et al. (2023).

        @return: O custo de CNOTs da porta.
        """
        n = len(self.controles)
        return 2 * n ** 2 - 2 * n + 1

    def calcula_custo_quantico(self):
        """
            https://reversiblebenchmarks.github.io/definitions.html
            https://physics.stackexchange.com/a/236054
            Rahman, Md Zamilur, and Jacqueline E. Rice. "Templates for positive and negative control Toffoli networks."
            International Conference on Reversible Computation. Springer, Cham, 2014.
                https://opus.uleth.ca/bitstream/handle/10133/3727/RAHMAN_MD_ZAMILUR_MSC_2015.pdf
            
            -- POSITIVE --
            n = 1 ==> QC =   1
            n = 2 ==> QC =   1
            n = 3 ==> QC =   5
            n = 4 ==> QC =  13
            n = 5 ==> QC =  29
            n = 6 ==> QC =  61
            n = 7 ==> QC = 125
            n = 8 ==> QC = 253
            n = 9 ==> QC = 509
            n > 9 ==> QC = 2**n - 3
            
            -- NEGATIVE -- 
            n = 1 ==> QC =   1
            n = 2 ==> QC =   1+2
            n = 3 ==> QC =   5+1    (see below)
            n = 4 ==> QC =  13+2
            n = 5 ==> QC =  29+2
            n = 6 ==> QC =  61+2
            n = 7 ==> QC = 125+2
            n = 8 ==> QC = 253+2
            n = 9 ==> QC = 509+2
            n > 9 ==> QC = 2**n - 1
            
            -- observation:: n = 3
            == Rahman, Md Zamilur, and Jacqueline E. Rice (2.8.3. Quantum Cost)
            The cost of T (a, b, c) T (a, b) (Peres gate) or T (a, b) T (a, b, c) 
            (inverse of Peres gate) is set to be 4 instead of 5 + 1 = 6, as the 
            quantum implementation of each of these patterns was found with cost 4.
        """
        custo_total = 0
        n = self.tamanho_bits

        if n == 1:
            # not
            custo_total += 1

        elif n == 3:
            # ccnot
            custo_total += 5

            if self.todos_controles_negativos():
                custo_total += 1

        else:
            # toffoli generalizada
            custo_total = 2 ** n - 3

            if self.todos_controles_negativos():
                custo_total += 2

        return custo_total

    def todos_controles_negativos(self):
        for ctrl in self.controles:
            # se o sinal é positivo, retorna False
            if ctrl.eh_sinal_positivo():
                return False

        # se todos os sinais são negativos, retorna True
        return True

    def eh_porta_not(self):
        return len(self.controles) == 0

    def eh_adjacente(self, other):
        if self.obtem_alvos() != other.obtem_alvos():
            return False

        diff = self.diferenca_entre_controles(other)
        diffs = len(diff)

        # pode diferir apenas em uma linha; se não houver ctrls diff, não é
        if diffs == 0:
            return False

        # se  houver apenas um controle diff, é adjacente
        if diffs == 1:
            return True

        # se houver exatamente dois controles, verifique as linhas
        if diffs == 2:
            gc = diff[0]
            hc = diff[1]

            return gc.linha == hc.linha

        # se houver mais de 2 ctrls diff. não pode ser adjacente
        return False

    def diferenca_entre_controles(self, other):
        s1 = set(self.controles)
        s2 = set(other.controles)
        diff = s1.symmetric_difference(s2)
        return sorted(diff)

    def obtem_linhas_de_alvo_usadas(self):
        linhas_usadas = set()
        linhas_usadas.add(self.alvos.linha)
        return linhas_usadas

    def obtem_linhas_de_controle_usadas(self):
        linhas_usadas = set()

        for ctrl in self.controles:
            linha = ctrl.linha
            linhas_usadas.add(linha)

        return linhas_usadas

    def obtem_linhas_usadas(self):
        linhas_de_alvo = self.obtem_linhas_de_alvo_usadas()
        linhas_de_controle = self.obtem_linhas_de_controle_usadas()

        linhas_usadas = linhas_de_alvo.union(linhas_de_controle)

        return linhas_usadas

    def inverte_controle_nas_linhas(self, linhas):
        for linha in linhas:
            for ctrl in self.controles:
                if linha == ctrl.linha:
                    ctrl.inverte_sinal()

    def roda_porta_permutacao(self, elementos):
        for i in range(len(elementos)):
            elem = elementos[i]
            # print('ELEM_ANTES -->', elem)

            if self.__deve_aplicar(elem):
                elementos[i] = self.__aplica(elem)

    def roda_porta_tabela_verdade(self, tabela):
        # print('T', tabela)

        for linha_tabela in tabela:
            alvo = self.alvos

            # print('L1', linha_tabela)

            if self.__deve_aplicar(linha_tabela):
                # print('aplicou')
                linha_tabela[alvo.linha] = int(not linha_tabela[alvo.linha])
                # print('L2', linha_tabela)

    def __deve_aplicar(self, elementos):
        for ctrl in self.controles:
            linha = ctrl.linha
            linha_mapeada = self.mapeamento[linha]
            valor = int(elementos[linha_mapeada])

            if ctrl.eh_sinal_positivo() and valor == 0:
                return False

            if ctrl.eh_sinal_negativo() and valor == 1:
                return False

        return True

    def __aplica(self, e):
        el = list(e)
        # print('\t\tVetor Elementos', el)

        linha_alvo = self.alvos.linha
        # print('\t\tLinha Alvo', linha_alvo)

        linha_alvo_mapeada = self.mapeamento[linha_alvo]
        # print('\t\tMapeamento', self.mapeamento)
        # print('\t\tLinha Alvo Mapeada', linha_alvo_mapeada)

        if el[linha_alvo_mapeada] == '0':
            el[linha_alvo_mapeada] = '1'
        elif el[linha_alvo_mapeada] == '1':
            el[linha_alvo_mapeada] = '0'
        else:
            raise Exception('Algum erro ocorreu!')

        resultado = ''.join(el)
        # print('ELEM_DEPOIS-->', resultado)

        return resultado

    def __repr__(self):
        s = f'T{self.tamanho_bits} '

        for ctrl in sorted(self.controles):
            s += f'{ctrl},'

        s += f'{self.alvos}'

        return s

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.obtem_alvos() != other.obtem_alvos():
            return False

        if len(self.controles) != len(other.controles):
            return False

        if self.controles != other.controles:
            return False

        return True

    def __hash__(self):
        return id(self.alvos) * hash(self.controles) * self.tamanho_bits

    def __len__(self):
        return self.tamanho_bits
