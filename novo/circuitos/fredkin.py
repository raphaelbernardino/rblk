class Fredkin:
    def __init__(self, alvos, controles):
        alvos.sort()
        self.alvos = alvos
        self.controles = controles
        self.tamanho_bits = len(alvos) + len(controles)

        if len(alvos) != 2:
            raise Exception('Alvos inválidos! São necessários dois alvos.')

    def calcula_custo_quantico(self):
        """
        https://reversiblebenchmarks.github.io/definitions.html

        The cost of a size n Fredkin gate is calculated as the cost of size n Toffoli gate plus 2, as the size n Fredkin gate can be efficiently simulated
        by a size n Toffoli gate and 2 CNOTs.
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
            custo_total += 2 ** n - 3

            if self.todos_controles_negativos():
                custo_total += 2

        return custo_total + 2

    def todos_controles_negativos(self):
        for ctrl in self.controles:
            # se o sinal é positivo, retorna False
            if ctrl.eh_sinal_positivo():
                return False

        # se todos os sinais são negativos, retorna True
        return True

    def obtem_linhas_de_alvo_usadas(self):
        linhas_usadas = set()

        linhas_usadas.add(self.alvos[0].linha)
        linhas_usadas.add(self.alvos[1].linha)

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
            if self.__deve_aplicar(elem):
                elementos[i] = self.__aplica(elem)

    def __deve_aplicar(self, e):
        aplica = True

        for ctrl in self.controles:
            sinal = ctrl.sinal
            linha = ctrl.linha

            if sinal and e[linha] != '1':
                aplica = False
            elif not sinal and e[linha] != '0':
                aplica = False

        return aplica

    def __aplica(self, e):
        linha_alvo1 = self.alvos[0].linha
        linha_alvo2 = self.alvos[1].linha

        el = list(e)
        el[linha_alvo1], el[linha_alvo2] = el[linha_alvo2], el[linha_alvo1]

        return ''.join(el)

    def __repr__(self):
        s = f'F{self.tamanho_bits} '

        for ctrl in self.controles:
            s += f'{ctrl},'

        s += f'{self.alvos[0]}, {self.alvos[1]}'

        return s

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        if self.alvos != other.alvos:
            return False

        if len(self.controles) != len(other.controles):
            return False

        if self.controles != other.controles:
            return False

        return True

    def __hash__(self):
        return (id(self.alvos[0]) + id(self.alvos[1])) * hash(self.controles) * self.tamanho_bits

    def __len__(self):
        return self.tamanho_bits
