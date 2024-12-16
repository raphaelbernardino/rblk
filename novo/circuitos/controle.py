from novo.circuitos.states import States


class Controle:
    def __init__(self, linha, sinal, mapa=None):
        self.linha_original = int(linha)

        if mapa is None:
            self.linha = int(linha)
        else:
            if linha >= len(mapa):
                self.linha = linha
            else:
                self.linha = int(mapa[linha])

        if isinstance(sinal, bool):
            self.sinal = sinal

        elif isinstance(sinal, States):
            self.sinal = bool(sinal.value)

        else:
            raise Exception('Sinal inválido! Não é booleano.')

        if self.linha < 0:
            raise Exception('Controle inválido! Linha negativa.')

    def modifica_linha(self, modificacao: int):
        """
        Modifica a linha atual. Para aumentar a linha informe um valor positivo, e para diminuir, um valor negativo.

        modificacao: int
        """
        self.linha = self.linha + modificacao

    def remapeia(self, mapa):
        self.linha = mapa[self.linha]

    def eh_sinal_positivo(self):
        return self.sinal == States.ctrl_positivo

    def eh_sinal_negativo(self):
        return self.sinal == States.ctrl_negativo

    def inverte_sinal(self):
        self.sinal = not self.sinal

    def possui_sinal_inverso(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.linha != other.linha:
            return False

        if self.sinal == other.sinal:
            return False

        return True

    def __repr__(self):
        s = "" if self.sinal else "'"
        return f'b{self.linha}{s}'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.sinal != other.sinal:
            return False

        if self.linha != other.linha:
            return False

        return True

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise Exception('Não é possível comparar Controle com outro tipo.')

        return self.linha < other.linha

    def __hash__(self):
        return id(self.sinal) * hash(self.linha + 1)
